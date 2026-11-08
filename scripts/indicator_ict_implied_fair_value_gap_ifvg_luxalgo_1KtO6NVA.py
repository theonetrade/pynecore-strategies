"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, bar_index, box, close, color, high, input, line, low,
    math, na, open, plot, script, ta
)
from pynecore.types import Persistent, Series


@script.indicator('ICT Implied Fair Value Gap (IFVG) [LuxAlgo]', overlay=True, max_lines_count=500, max_boxes_count=500)
def main(
    __input_0__=input.float(30, 'Shadow Threshold %', minval=0, maxval=100),
    ext=input(8, 'IFVG Extension'),
    extAvg=input(False, 'Extend Averages'),
    showBull=input(True, 'Bullish IFVG', inline='bull', group='Style'),
    bullZone=input(color.new(color.new('#3179F5'), 50), '', inline='bull', group='Style'),
    bullAvg=input(color.new('#3179F5'), '', inline='bull', group='Style'),
    showBear=input(True, 'Bearish IFVG', inline='bear', group='Style'),
    bearZone=input(color.new(color.new('#FF5D00'), 50), '', inline='bear', group='Style'),
    bearAvg=input(color.new('#FF5D00'), '', inline='bear', group='Style')
):
    thr = __input_0__ / 100
    n = bar_index
    r = high - low
    b: Series = math.abs(close - open)
    bull_top = math.avg(math.min(close, open), low)
    bull_btm = math.avg(math.max(close[2], open[2]), high[2])
    bull_ifvg = b[1] > math.max(b, b[2]) and low < high[2] and ((math.min(close, open) - low) / r > thr) and ((high[2] - math.max(close[2], open[2])) / r > thr) and (bull_top > bull_btm)
    bear_top = math.avg(math.min(close[2], open[2]), low[2])
    bear_btm = math.avg(math.max(close, open), high)
    bear_ifvg = b[1] > math.max(b, b[2]) and high > low[2] and ((high - math.max(close, open)) / r > thr) and ((math.min(close[2], open[2]) - low[2]) / r > thr) and (bear_top > bear_btm)
    bull_ifvg_avg: Persistent[float] = na(float)
    bear_ifvg_avg: Persistent[float] = na(float)
    if bull_ifvg and showBull:
        bull_ifvg_avg = math.avg(bull_top, bull_btm)
        box.new(n - 2, bull_top, n + ext, bull_btm, border_color=bullAvg, bgcolor=bullZone)
        line.new(n - 2, bull_ifvg_avg, n + ext, bull_ifvg_avg, color=bullAvg)
    if bear_ifvg and showBear:
        bear_ifvg_avg = math.avg(bear_top, bear_btm)
        box.new(n - 2, bear_top, n + ext, bear_btm, border_color=bearAvg, bgcolor=bearZone)
        line.new(n - 2, bear_ifvg_avg, n + ext, bear_ifvg_avg, color=bearAvg)
    plot(bull_ifvg_avg, 'Bullish IFVG Average', bullAvg if ta.barssince(bull_ifvg) > ext and extAvg else na)
    plot(bear_ifvg_avg, 'Bearish IFVG Average', bearAvg if ta.barssince(bear_ifvg) > ext and extAvg else na)
    alertcondition(bull_ifvg, 'Bullish IFVG', 'Bullish IFVG detected')
    alertcondition(bear_ifvg, 'Bearish IFVG', 'Bearish IFVG detected')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
