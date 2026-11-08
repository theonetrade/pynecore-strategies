"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_method import method
from pynecore.core.series import inline_series
from pynecore.lib import (
    alertcondition, bar_index, barcolor, close, color, display, fill, high,
    hlc3, input, label, low, math, na, open, plot, plotcandle, script, size, ta
)
from pynecore.types import PersistentSeries, Series

RSI_group: str = 'RMI Settings'
visual: str = 'Visuals'


@script.indicator('RMI Trend Sniper', overlay=True, max_labels_count=500, na_bool=True)
def main(
    Length=input(14, 'RMI Length ', inline='RMI', group=RSI_group),
    pmom=input(66, ' Positive above', inline='rsi1', group=RSI_group),
    nmom=input(30, 'Negative below', inline='rsi1', group=RSI_group),
    filleshow=input(True, 'Show Range MA ', inline='002', group=visual),
    bull=input(color.new('#00BCD4'), '', inline='002', group=visual),
    bear=input(color.new('#FF5252'), '', inline='002', group=visual)
):
    positive: PersistentSeries[bool] = False
    negative: PersistentSeries[bool] = False
    mom_group: str = 'Range Vales'
    BarRange: float = high - low
    up = ta.rma(math.max(ta.change(close), 0), Length)
    down = ta.rma(-math.min(ta.change(close), 0), Length)
    rsi = 100 if down == 0 else 0 if up == 0 else 100 - 100 / (1 + up / down)
    mf = ta.mfi(hlc3, Length)
    rsi_mfi: Series = math.avg(rsi, mf)
    ema_1 = ta.ema(close, 5)
    change_1 = ta.change(ema_1)
    p_mom: bool = rsi_mfi[1] < pmom and rsi_mfi > pmom and (rsi_mfi > nmom) and (change_1 > 0)
    ema_2 = ta.ema(close, 5)
    change_2 = ta.change(ema_2)
    n_mom: bool = rsi_mfi < nmom and change_2 < 0
    if p_mom:
        positive = True
        negative = False
    if n_mom:
        positive = False
        negative = True
    @method
    def _Band(len: int):
        return inline_series(math.min(ta.atr(len) * 0.3, close * (0.3 / 100)), 20) / 2 * 8

    Band = _Band(30)
    @method
    def rangeMA(Range: float, Prd):
        weight = Range / math.sum(Range, Prd)
        sum = math.sum(close * weight, Prd)
        tw = math.sum(weight, Prd)
        return sum / tw

    rwma = rangeMA(BarRange, 20)
    colour = bull if positive else bear
    RWMA = rwma - Band if positive else rwma + Band if negative else na
    alpha = color.new(color.black, 100)
    center = plot(RWMA if filleshow else na, 'RRTH', colour, editable=True)
    plot(RWMA if filleshow else na, 'RRTH', color.new(colour, 70), 2, editable=True)
    plot(RWMA if filleshow else na, 'RRTH', color.new(colour, 80), 3, editable=True)
    plot(RWMA if filleshow else na, 'RRTH', color.new(colour, 90), 4, editable=True)
    plot(close, 'CLOSE', colour, editable=False, display=display.pane)
    max = RWMA + Band
    min = RWMA - Band
    top = plot(max if filleshow else na, 'RRTH', alpha)
    bottom = plot(min if filleshow else na, 'RRTH', alpha)
    fill(top, center, top_value=max, bottom_value=RWMA, bottom_color=color.new(colour, 75), top_color=alpha, editable=True)
    fill(center, bottom, top_value=RWMA, bottom_value=min, bottom_color=alpha, top_color=color.new(colour, 75), editable=True)
    Barcol = color.green if positive else color.red
    if negative and (not negative[1]):
        label.new(bar_index, max + Band / 2, '', color=color.red, size=size.small)
    if positive and (not positive[1]):
        label.new(bar_index, min - Band / 2, '', color=color.green, size=size.small, style=label.style_label_up)
    plotcandle(open, high, low, close, color=Barcol, wickcolor=Barcol, bordercolor=Barcol)
    barcolor(color=Barcol)
    alertcondition(positive and (not positive[1]), 'BUY')
    alertcondition(negative and (not negative[1]), 'SELL')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
