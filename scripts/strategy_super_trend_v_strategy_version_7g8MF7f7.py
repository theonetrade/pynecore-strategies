"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    close, color, fill, high, input, location, low, math, na, nz, open, plot,
    plotshape, script, shape, size, strategy, ta, time, timeframe, timestamp, volume
)
from pynecore.types import Persistent, Series


@script.strategy(title='Super trend V Strategy version', overlay=True, pyramiding=1, initial_capital=1000, default_qty_type=strategy.percent_of_equity, default_qty_value=100, calc_on_order_fills=False, slippage=0, commission_type=strategy.commission.percent, commission_value=0.075, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    strat_dir_input=input.string(title='Strategy Direction', defval='long', options=('long', 'short', 'all')),
    tf=input(720),
    st_mult=input.float(1, title='SuperTrend Multiplier', minval=0, maxval=100, step=0.01),
    st_period=input.int(10, title='SuperTrend Period', minval=1),
    multiplier=input.float(title='TP VWAP Deviation', defval=2, minval=1),
    len5=input.int(title='TP length', defval=150, minval=1),
    testStartYear=input(2016, 'Backtest Start Year'),
    testStartMonth=input(1, 'Backtest Start Month'),
    testStartDay=input(1, 'Backtest Start Day'),
    testStopYear=input(2030, 'Backtest Stop Year'),
    testStopMonth=input(12, 'Backtest Stop Month'),
    testStopDay=input(30, 'Backtest Stop Day')
):
    strat_dir_value = strategy.direction.long if strat_dir_input == 'long' else strategy.direction.short if strat_dir_input == 'short' else strategy.direction.all
    strategy.risk.allow_entry_in(strat_dir_value)
    hilow = (high - low) * 100
    openclose = (close - open) * 100
    vol = volume / hilow
    spreadvol = openclose * vol
    VPT = spreadvol + ta.cum(spreadvol)
    window_len: int = 28
    v_len: int = 14
    price_spread = ta.stdev(high - low, window_len)
    v = spreadvol + ta.cum(spreadvol)
    smooth = ta.sma(v, v_len)
    v_spread = ta.stdev(v - smooth, window_len)
    shadow = (v - smooth) / v_spread * price_spread
    out = high + shadow if shadow > 0 else low + shadow
    src = out
    src1 = open
    src2 = low
    src3 = high
    len = tf / timeframe.multiplier * 7 if timeframe.isintraday and timeframe.multiplier >= 1 else 60 / timeframe.multiplier * 24 * 7 if timeframe.isintraday and timeframe.multiplier < 60 else 7
    c = ta.ema(src, len)
    plot(c, color=color.new(color.red, 0))
    o = ta.ema(src1, len)
    plot(o, color=color.new(color.blue, 0))
    col = color.lime if c > o else color.orange
    vis: bool = True
    vl = c
    ll = o
    m1 = plot(vl, color=col, linewidth=1)
    m2 = plot(ll if vis else na, color=col, linewidth=2)
    fill(m1, m2, color=color.new(col, 70))
    vpt = ta.ema(out, len)
    up_lev = vpt - st_mult * ta.atr(st_period)
    dn_lev = vpt + st_mult * ta.atr(st_period)
    up_trend: Series[float] = 0.0
    up_trend = math.max(up_lev, up_trend[1]) if close[1] > up_trend[1] else up_lev
    down_trend: Series[float] = 0.0
    down_trend = math.min(dn_lev, down_trend[1]) if close[1] < down_trend[1] else dn_lev
    trend: Series[int] = 0
    trend = 1 if close > down_trend[1] else -1 if close < up_trend[1] else nz(trend[1], 1)
    st_line: Series = up_trend if trend == 1 else down_trend
    plot(st_line[1], color=color.green if trend == 1 else color.red, style=plot.style_cross, linewidth=2, title='SuperTrend')
    buy = ta.crossover(close, st_line) and close > o
    sell = ta.crossunder(close, st_line) and close < o
    plotshape(buy, title='buy', text='Buy', color=color.new(color.green, 0), style=shape.labelup, location=location.belowbar, size=size.small, textcolor=color.new(color.white, 0))
    plotshape(sell, title='sell', text='Sell', color=color.new(color.red, 0), style=shape.labeldown, location=location.abovebar, size=size.small, textcolor=color.new(color.white, 0))
    src5 = ta.vwap
    offset: int = 0
    def calcSlope(src5: Series, len5):
        sumX: float = 0.0
        sumY: float = 0.0
        sumXSqr: float = 0.0
        sumXY: float = 0.0
        for i__00000032__ in pine_range(1, len5, 1):
            val = src5[len5 - i__00000032__]
            per = i__00000032__ + 1.0
            sumX = sumX + per
            sumY = sumY + val
            sumXSqr = sumXSqr + per * per
            sumXY = sumXY + val * per
        slope = (len5 * sumXY - sumX * sumY) / (len5 * sumXSqr - sumX * sumX)
        average = sumY / len5
        intercept = average - slope * sumX / len5 + slope
        return (slope, average, intercept)

    tmp: Persistent[float] = na(float)
    s, a, i = calcSlope(src5, len5)
    vwap1 = i + s * (len5 - offset)
    sdev = ta.stdev(ta.vwap, len5)
    dev = multiplier * sdev
    top = vwap1 + dev
    bott = vwap1 - dev
    z1 = vwap1 + dev
    x1 = vwap1 - dev
    low1 = ta.crossover(close, x1)
    high1 = ta.crossunder(close, z1)
    plotshape(low1, title='low', text='TP', color=color.new(color.red, 0), style=shape.labelup, location=location.belowbar, size=size.small, textcolor=color.new(color.white, 0))
    plotshape(high1, title='high', text='TP', color=color.new(color.green, 0), style=shape.labeldown, location=location.abovebar, size=size.small, textcolor=color.new(color.white, 0))
    testPeriodStart = timestamp(testStartYear, testStartMonth, testStartDay, 0, 0)
    testPeriodStop = timestamp(testStopYear, testStopMonth, testStopDay, 0, 0)
    def testPeriod():
        return True if time >= testPeriodStart and time <= testPeriodStop else False

    l = buy
    s1 = sell
    testPeriod_1 = testPeriod()
    if l and testPeriod_1:
        strategy.entry('buy', strategy.long)
    testPeriod_2 = testPeriod()
    if s1 and testPeriod_2:
        strategy.entry('sell', strategy.short)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
