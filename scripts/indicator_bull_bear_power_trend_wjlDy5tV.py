"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bar_index, close, color, fill, high, hline, input, low, na, plot, script,
    ta
)


@script.indicator('BULL BEAR POWER TREND', shorttitle='BBPT', overlay=False, na_bool=True)
def main(
    reg_trend_on=input(False, 'Activate Reg Trend Line'),
    length=input.int(defval=8, title='🔹 Length Reg Trend line=', minval=1)
):
    BullTrend_hist: float = 0.0
    BearTrend_hist: float = 0.0
    BullTrend = (close - ta.lowest(low, 50)) / ta.atr(5)
    BearTrend = (ta.highest(high, 50) - close) / ta.atr(5)
    BearTrend2 = -1 * BearTrend
    Trend = BullTrend - BearTrend
    hline(0, title='Nivel 0', color=color.new('#000000'), linestyle=hline.style_solid, linewidth=1)
    niv_0 = plot(0, title='Nivel 0"', color=color.new(color.new('#000000'), 100), linewidth=1, style=plot.style_line)
    hline(2, title='Nivel 2', color=color.new('#008000'), linestyle=hline.style_solid, linewidth=1)
    niv_2 = plot(2, title='Nivel 2', color=color.new(color.new('#008000'), 100), linewidth=1, style=plot.style_line)
    hline(-2, title='Nivel -2', color=color.new('#FF0000'), linestyle=hline.style_solid, linewidth=1)
    niv_22 = plot(-2, title='Nivel -2"', color=color.new(color.new('#FF0000'), 100), linewidth=1, style=plot.style_line)
    a = plot(BullTrend, title='Bull Trend"', color=color.new(color.new('#008000'), 0), linewidth=2, style=plot.style_line)
    b = plot(BearTrend2, title='Bear Trend"', color=color.new(color.new('#FF0000'), 0), linewidth=2, style=plot.style_line)
    fill(a, niv_2, color=color.new(color.new('#008000'), 50))
    fill(b, niv_22, color=color.new(color.new('#FF0000'), 50))
    fill(niv_22, niv_2, color=color.new(color.white, 60))
    plot(Trend if reg_trend_on == False else na, title='Trend', color=color.new(color.new('#000000'), 0), linewidth=1, style=plot.style_line)
    if BullTrend < 2:
        BullTrend_hist = BullTrend - 2
    plot(BullTrend_hist, title='Bull Trend Hist', color=color.new(color.new('#FF0000'), 0), linewidth=1, style=plot.style_columns)
    if BearTrend2 > -2:
        BearTrend_hist = BearTrend2 + 2
    plot(BearTrend_hist, title='Bull Trend Hist', color=color.new(color.new('#008000'), 0), linewidth=1, style=plot.style_columns)
    x = bar_index
    y = Trend
    x_ = ta.sma(x, length)
    y_ = ta.sma(y, length)
    mx = ta.stdev(x, length)
    my = ta.stdev(y, length)
    c = ta.correlation(x, y, length)
    slope = c * (my / mx)
    inter = y_ - slope * x_
    reg_trend = x * slope + inter
    plot(reg_trend if reg_trend_on == True else na, title='Trend', color=color.new(color.new('#000000'), 0), linewidth=1, style=plot.style_line)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
