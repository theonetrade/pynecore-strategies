"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    close, color, fill, high, hline, input, low, math, na, open, plot,
    plotcandle, script, strategy, syminfo, ta
)


@script.strategy(title='Simple RSI strategy', overlay=False, pyramiding=5, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value=20, commission_type=strategy.commission.percent, commission_value=0.075, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    OverBought=input.int(80, minval=50),
    OverSold=input.int(25, maxval=50),
    len=input.int(5, minval=1, title='RSI Length'),
    ProfitTarget_Percent=input(3),
    LossTarget_Percent=input(10)
):
    SWperiod: int = 1
    look: int = 0
    bandmx = hline(100)
    bandmn = hline(0)
    band1 = hline(OverBought)
    band0 = hline(OverSold)
    fill(band1, band0, color=color.new(color.purple, 98))
    src = close
    up = ta.rma(math.max(ta.change(src), 0), len)
    down = ta.rma(-math.min(ta.change(src), 0), len)
    rsi = 100 if down == 0 else 0 if up == 0 else 100 - 100 / (1 + up / down)
    p: int = 100
    hh = ta.highest(high, p)
    ll = ta.lowest(low, p)
    scale__ren__ = hh - ll
    dyno = (open - ll) / scale__ren__ * 100
    dynl = (low - ll) / scale__ren__ * 100
    dynh = (high - ll) / scale__ren__ * 100
    dync = (close - ll) / scale__ren__ * 100
    color_1 = 1 if close > open else 0
    hline(78.6)
    hline(61.8)
    hline(50)
    hline(38.2)
    hline(23.6)
    plotcandle(dyno, dynh, dynl, dync, title='Candle', color=color.green if color_1 == 1 else color.red)
    plot(10, color=color.new(color.green, 0))
    plot(55, color=color.new(color.black, 0))
    plot(80, color=color.new(color.black, 0))
    plot(90, color=color.new(color.red, 0))
    long = 5 if rsi <= OverSold else na
    golong = 5 if rsi <= OverSold else na
    longsignal = golong
    Profit_Ticks = close * (ProfitTarget_Percent / 100) / syminfo.mintick
    Loss_Ticks = close * (LossTarget_Percent / 100) / syminfo.mintick
    if strategy.opentrades == 0 and cast_bool(longsignal):
        strategy.entry('Entry 1', strategy.long)
    if strategy.opentrades == 1 and cast_bool(longsignal):
        strategy.entry('Entry 2', strategy.long)
    if strategy.opentrades == 2 and cast_bool(longsignal):
        strategy.entry('Entry 3', strategy.long)
    if strategy.opentrades == 3 and cast_bool(longsignal):
        strategy.entry('Entry 4', strategy.long)
    if strategy.opentrades == 4 and cast_bool(longsignal):
        strategy.entry('Entry 5', strategy.long)
    if strategy.opentrades == 5 and cast_bool(longsignal):
        strategy.entry('Entry 6', strategy.long)
    if strategy.opentrades == 6 and cast_bool(longsignal):
        strategy.entry('Entry 7', strategy.long)
    if strategy.position_size > 0:
        strategy.exit(id='Exit 1', from_entry='Entry 1', profit=Profit_Ticks, loss=Loss_Ticks)
        strategy.exit(id='Exit 2', from_entry='Entry 2', profit=Profit_Ticks, loss=Loss_Ticks)
        strategy.exit(id='Exit 3', from_entry='Entry 3', profit=Profit_Ticks, loss=Loss_Ticks)
        strategy.exit(id='Exit 4', from_entry='Entry 4', profit=Profit_Ticks, loss=Loss_Ticks)
        strategy.exit(id='Exit 5', from_entry='Entry 5', profit=Profit_Ticks, loss=Loss_Ticks)
        strategy.exit(id='Exit 6', from_entry='Entry 6', profit=Profit_Ticks, loss=Loss_Ticks)
        strategy.exit(id='Exit 7', from_entry='Entry 7', profit=Profit_Ticks, loss=Loss_Ticks)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
