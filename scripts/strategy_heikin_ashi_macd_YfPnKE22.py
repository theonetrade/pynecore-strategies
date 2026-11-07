"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, dayofmonth, fill, high, hline, input, low, math, month, na,
    open, plot, script, strategy, syminfo, ta, year
)
from pynecore.types import Series


@script.strategy('MACD ASHI BARS Wıth SL-TP ', overlay=False, default_qty_type=strategy.percent_of_equity, default_qty_value=100, commission_type=strategy.commission.percent, commission_value=0.1, slippage=1, margin_long=0, margin_short=0, initial_capital=100000, close_by_id=True, na_bool=True)
def main(
    target_profit_percent=input(10, 'target profit%'),
    stop_loss_percent=input(3, 'stop loss %'),
    fastmacd=input(12, title='MACD Fast  Line Length'),
    slowmacd=input(25, title='MACD Slow Line Length'),
    signalmacd=input(15, title='Signal Line Length'),
    yearfrom=input(2020),
    yearuntil=input(2022),
    monthfrom=input(1),
    monthuntil=input(12),
    dayfrom=input(1),
    dayuntil=input(31)
):
    haopen: Series[float] = 0.0
    haclose: Series = (open + high + low + close) / 4
    haopen = (open + close) / 2 if na(haopen[1]) else (haopen[1] + haclose[1]) / 2
    hahigh = math.max(high, math.max(haopen, haclose))
    halow = math.min(low, math.min(haopen, haclose))
    hacolor = color.green if haclose > haopen else color.red
    src = haclose
    macdslowline1 = ta.sma(src, slowmacd)
    macdslowline2 = ta.sma(macdslowline1, slowmacd)
    DEMAslow = 2 * macdslowline1 - macdslowline2
    macdfastline1 = ta.sma(src, fastmacd)
    macdfastline2 = ta.sma(macdfastline1, fastmacd)
    DEMAfast = 2 * macdfastline1 - macdfastline2
    MACDLine = DEMAfast - DEMAslow
    SignalLine = ta.sma(MACDLine, signalmacd)
    delta = MACDLine - SignalLine
    swap1 = color.green if delta > 0 else color.red
    plot(delta, color=swap1, style=plot.style_columns, title='Histo', histbase=0)
    p1 = plot(MACDLine, color=color.new(color.blue, 0), title='MACD Line')
    p2 = plot(SignalLine, color=color.new(color.red, 0), title='Signal')
    fill(p1, p2, color=color.new(color.blue, 90))
    hline(0)
    if ta.crossover(delta, 0) and year >= yearfrom and (year <= yearuntil) and (month >= monthfrom) and (month <= monthuntil) and (dayofmonth >= dayfrom) and (dayofmonth < dayuntil):
        strategy.entry('LONG', strategy.long, stop=close, oca_name='TREND', oca_type=strategy.oca.cancel, comment='LONG')
    else:
        strategy.cancel(id='LONG')
    if ta.crossunder(delta, 0) and year >= yearfrom and (year <= yearuntil) and (month >= monthfrom) and (month <= monthuntil) and (dayofmonth >= dayfrom) and (dayofmonth < dayuntil):
        strategy.entry('SHORT', strategy.short, stop=close, oca_name='TREND', oca_type=strategy.oca.cancel, comment='SHORT')
    else:
        strategy.cancel(id='SHORT')
    profit_target = close * (target_profit_percent / 100) / syminfo.mintick
    stop_target = close * (stop_loss_percent / 100) / syminfo.mintick
    strategy.exit('LONG EXIT', 'LONG', profit=profit_target, loss=stop_target)
    strategy.exit('LONG EXIT', 'SHORT', profit=profit_target, loss=stop_target)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
