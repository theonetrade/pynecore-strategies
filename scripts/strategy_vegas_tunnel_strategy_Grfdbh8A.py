"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, fill, high, input, low, plot, request, script, strategy,
    syminfo, ta, time, timeframe, timestamp
)
from pynecore.types import Series


@script.strategy('Vegas Tunnel strategy', overlay=True, pyramiding=20, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    useCurrentRes=input(True, title='Use Current Chart Resolution?'),
    resCustom=input.timeframe(title='Use Different Timeframe? Uncheck Box Above', defval='D'),
    maPeriods2=input(12, '12 EMA'),
    maPeriods6=input(240, '240 SMA'),
    BBlength=input.int(20, title='BB Length', minval=1),
    BBsrc: Series[float] = input(close, title='BB Source'),
    mult=input.float(2.0, minval=0.001, maxval=50, title='BB StdDev'),
    offset=input.int(0, 'BB Offset', minval=-500, maxval=500),
    startDate=input.int(title='Start Date', defval=1, minval=1, maxval=31),
    startMonth=input.int(title='Start Month', defval=1, minval=1, maxval=12),
    startYear=input.int(title='Start Year', defval=2018, minval=1800, maxval=2100),
    endDate=input.int(title='End Date', defval=1, minval=1, maxval=31),
    endMonth=input.int(title='End Month', defval=11, minval=1, maxval=12),
    endYear=input.int(title='End Year', defval=2030, minval=1800, maxval=2100)
):
    tfSet = timeframe.period if useCurrentRes else resCustom
    sm2 = request.security(syminfo.tickerid, tfSet, ta.ema(close, maPeriods2))
    sm6 = request.security(syminfo.tickerid, tfSet, ta.sma(close, maPeriods6))
    p2 = plot(sm2, color=color.new(color.green, 30), linewidth=2, title='SMA2')
    p6 = plot(sm6, color=color.new(color.white, 30), linewidth=2, title='SMA6')
    basis = ta.sma(BBsrc, BBlength)
    dev = mult * ta.stdev(BBsrc, BBlength)
    upper = basis + dev
    lower = basis - dev
    pBB1 = plot(upper, 'Upper', color=color.new(color.blue, 0), offset=offset)
    pBB2 = plot(lower, 'Lower', color=color.new(color.blue, 0), offset=offset)
    fast_ma = ta.ema(close, 48)
    slow_ma = ta.ema(close, 56)
    macd = fast_ma - slow_ma
    f1 = ta.ema(close, 36)
    f2 = ta.ema(close, 43)
    f3 = ta.ema(close, 144)
    f4 = ta.ema(close, 169)
    f5 = ta.ema(close, 576)
    f6 = ta.ema(close, 676)
    f7 = ta.ema(close, 2304)
    z1 = plot(f1, color=color.new(color.red, 100), title='ema36')
    z2 = plot(f2, color=color.new(color.red, 100), title='ema43')
    z3 = plot(f3, color=color.new(color.green, 100), title='ema144')
    z4 = plot(f4, color=color.new(color.green, 100), title='ema169')
    z5 = plot(f5, color=color.new(color.white, 100), title='ema576')
    z6 = plot(f6, color=color.new(color.white, 100), title='ema676')
    fill(z1, z2, color=color.new(color.red, 60))
    fill(z3, z4, color=color.new(color.green, 60))
    fill(z5, z6, color=color.new(color.gray, 60))
    inDateRange = time >= timestamp(syminfo.timezone, startYear, startMonth, startDate, 0, 0) and time < timestamp(syminfo.timezone, endYear, endMonth, endDate, 0, 0)
    crossunder_1 = ta.crossunder(f3, f1)
    if inDateRange and crossunder_1:
        if macd > 0:
            strategy.entry('buy', strategy.long, 100, comment='買Long-term')
    buyclose = ta.crossunder(f3, f5)
    if buyclose:
        strategy.close('buy', comment='關Long-term')
    crossover_1 = ta.crossover(low, f3)
    if inDateRange and crossover_1 and (macd > 0) and (f3 > f6):
        strategy.entry('buy1', strategy.long, 100, comment='買Mid-term')
    buyclose1 = ta.crossunder(close, upper * 0.999)
    if macd < 0 or f3 < f6:
        strategy.close('buy1', comment='關Mid-term')
    if buyclose1:
        strategy.close('buy1', comment='關Mid-term', qty_percent=100)
    crossunder_2 = ta.crossunder(low, f1)
    if inDateRange and macd > 0 and crossunder_2 and (f1 > f4):
        strategy.entry('buy3', strategy.long, 100, comment='買Short-term')
    buyclose3 = ta.crossunder(close, upper * 0.999)
    if macd < 0 or f1 < f4:
        strategy.close('buy3', comment='關Short-term')
    if buyclose3:
        strategy.close('buy3', comment='關Short-term')
    crossunder_3 = ta.crossunder(low, f5)
    if inDateRange and macd > 0 and crossunder_3 and (f4 > f5):
        strategy.entry('buy4', strategy.long, 100, comment='買Long-term')
    buyclose4 = ta.crossunder(close, upper * 0.999)
    if macd < 0 or f4 < f6:
        strategy.close('buy4', comment='關Long-term')
    if buyclose4:
        strategy.close('buy4', comment='關Long-term')
    crossunder_4 = ta.crossunder(high, f1)
    if inDateRange and macd < 0 and crossunder_4 and (f1 < f3) and (f3 < f6):
        strategy.entry('sell1', strategy.short, 100, comment='空Short-term')
    sellclose1 = ta.crossunder(lower * 0.999, close)
    if macd > 0 or f1 > f4:
        strategy.close('sell1', comment='關空Short-term')
    if sellclose1:
        strategy.close('sell1', comment='關空Short-term')
    crossunder_5 = ta.crossunder(high, f4)
    if inDateRange and macd < 0 and crossunder_5 and (f4 < f6):
        strategy.entry('sell2', strategy.short, 100, comment='空Mid-term')
    sellclose2 = ta.crossunder(lower, close)
    if macd > 0 or f4 > f6:
        strategy.close('sell2', comment='關空Mid-term')
    if sellclose2:
        strategy.close('sell2', comment='關Mid-term')
    crossunder_6 = ta.crossunder(high, f6)
    if inDateRange and macd < 0 and crossunder_6:
        strategy.entry('sell3', strategy.short, 100, comment='空Long-term')
    sellclose3 = ta.crossunder(lower, close)
    if macd > 0 or f6 > f7:
        strategy.close('sell3', comment='關空Long-term')
    if sellclose3:
        strategy.close('sell3', comment='關空Long-term')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
