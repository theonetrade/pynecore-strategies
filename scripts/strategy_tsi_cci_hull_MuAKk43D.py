"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.series import inline_series
from pynecore.lib import color, fill, input, math, na, open, plot, script, strategy, ta
from pynecore.types import Series


@script.strategy(title='TSI CCI Hull', shorttitle='TSICCIHULL', default_qty_type=strategy.percent_of_equity, default_qty_value=100, calc_on_order_fills=False, calc_on_every_tick=True, pyramiding=0, margin_long=0, margin_short=0, initial_capital=100000, close_by_id=True, na_bool=True)
def main(
    long=input(title='Long Length', defval=50),
    short=input(title='Short Length', defval=50),
    signal=input(title='Signal Length', defval=25),
    price: Series[float] = input(title='Source', defval=open),
    Period=input.int(25, minval=1),
    lineupper=input(title='Upper Line', defval=100),
    linelower=input(title='Lower Line', defval=-100)
):
    p = price
    length = Period
    def double_smooth(src, long, short):
        fist_smooth = ta.ema(src, long)
        return ta.ema(fist_smooth, short)

    pc = ta.change(price)
    double_smoothed_pc = double_smooth(pc, long, short)
    double_smoothed_abs_pc = double_smooth(math.abs(pc), long, short)
    tsi_value = 100 * (double_smoothed_pc / double_smoothed_abs_pc)
    keh = color.red if tsi_value * 5 > linelower else color.lime
    teh = color.red if ta.ema(tsi_value * 5, signal * 5) > lineupper else color.lime
    meh = color.red if ta.ema(tsi_value * 5, signal * 5) > tsi_value * 5 else color.lime
    i1 = plot(tsi_value * 5, title='TSI Value', color=color.new(color.black, 100), linewidth=1)
    i2 = plot(ta.ema(tsi_value * 5, signal * 5), title='TSI Signal', color=color.new(color.black, 100), linewidth=1)
    fill(i1, i2, color=color.new(meh, 85))
    plot(tsi_value * 5 if ta.cross(tsi_value * 5, ta.ema(tsi_value * 5, signal * 5)) else na, style=plot.style_circles, color=color.new(color.black, 0), linewidth=10)
    plot(tsi_value * 5 if ta.cross(tsi_value * 5, ta.ema(tsi_value * 5, signal * 5)) else na, style=plot.style_circles, color=color.new(color.white, 0), linewidth=8)
    plot(tsi_value * 5 if ta.cross(tsi_value * 5, ta.ema(tsi_value * 5, signal * 5)) else na, style=plot.style_circles, color=meh, linewidth=5)
    n2ma = 2 * ta.wma(p, math.round(length / 2))
    nma = ta.wma(p, length)
    diff = n2ma - nma
    sqn = math.round(math.sqrt(length))
    n1: Series = ta.wma(diff, sqn)
    cci: Series = (p - n1) / (0.015 * ta.dev(p, length))
    c = color.lime if cci > 0 else color.red
    c1 = color.lime if cci > 20 else color.silver
    c2 = color.red if cci < -20 else color.silver
    cc = plot(cci, color=c, title='CCI Line', linewidth=2)
    cc2 = plot(cci[1], color=color.new(color.gray, 100), linewidth=1)
    fill(cc, cc2, color=color.new(c, 85))
    plot(20 if ta.cross(20, cci) else na, style=plot.style_cross, title='CCI cross UP', color=c1, linewidth=2, offset=-2)
    plot(-20 if ta.cross(-20, cci) else na, style=plot.style_cross, title='CCI cross down', color=c2, linewidth=2, offset=-2)
    TSI1 = ta.ema(tsi_value * 5, signal * 5)
    TSI2 = inline_series(ta.ema(tsi_value * 5, signal * 5), 2)
    hullma_smoothed = ta.wma(2 * ta.wma(n1, Period / 2) - ta.wma(n1, Period), math.round(math.sqrt(Period)))
    longCondition = TSI1 > TSI2 and hullma_smoothed < price and (cci > 0)
    if longCondition and cci > cci[1] and (cci > 0) and (n1 > n1[1]):
        strategy.entry('Buy Here', strategy.long)
    shortCondition = TSI1 < TSI2 and hullma_smoothed > price and (cci < 0)
    if shortCondition and cci < cci[1] and (cci < 0) and (n1 < n1[1]):
        strategy.entry('Sell Here', strategy.short)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
