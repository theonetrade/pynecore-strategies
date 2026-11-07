"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, fill, hl2, input, location, math, nz, plot, plotshape,
    script, shape, size, strategy, ta, time, timestamp
)
from pynecore.types import Series


@script.strategy('SuperTrend Cloud Strategy', shorttitle='SuperTrend Cloud Strategy', overlay=True, default_qty_type=strategy.percent_of_equity, default_qty_value=100, initial_capital=1000, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    CrossExit=input(False, title='Exit on complete cross of cloud only?'),
    multi1=input.float(title='Multiplier 1', step=0.1, defval=2.4, minval=1),
    period1=input.int(title='Period 1', step=1, defval=4, minval=1),
    multi2=input.float(title='Multiplier 2', step=0.1, defval=4.8, minval=1),
    period2=input.int(title='Period 2', step=1, defval=4, minval=1),
    fromDay=input.int(defval=1, title='From Day', minval=1, maxval=31),
    fromMonth=input.int(defval=1, title='From Month', minval=1, maxval=12),
    fromYear=input.int(defval=2019, title='From Year', minval=1970),
    toDay=input.int(defval=1, title='To Day', minval=1, maxval=31),
    toMonth=input.int(defval=1, title='To Month', minval=1, maxval=12),
    toYear=input.int(defval=2020, title='To Year', minval=1970)
):
    startDate = timestamp(fromYear, fromMonth, fromDay, 0, 0)
    finishDate = timestamp(toYear, toMonth, toDay, 0, 0)
    time_cond = time >= startDate and time <= finishDate
    def getSuperTrend(multi, period):
        up_lev = hl2 - multi * ta.atr(period)
        dn_lev = hl2 + multi * ta.atr(period)
        up_trend: Series[float] = 0.0
        up_trend = math.max(up_lev, up_trend[1]) if close[1] > up_trend[1] else up_lev
        down_trend: Series[float] = 0.0
        down_trend = math.min(dn_lev, down_trend[1]) if close[1] < down_trend[1] else dn_lev
        trend: Series[int] = 0
        trend = 1 if close > down_trend[1] else -1 if close < up_trend[1] else nz(trend[1], 1)
        st_line = up_trend if trend == 1 else down_trend
        return (st_line, trend)

    st_line1, trend1 = getSuperTrend(multi1, period1)
    st_line2, trend2 = getSuperTrend(multi2, period2)
    plot1 = plot(st_line1, color=color.green if trend1 == 1 else color.red, style=plot.style_line, linewidth=1, title='SuperTrend 1')
    plot2 = plot(st_line2, color=color.green if trend2 == 1 else color.red, style=plot.style_line, linewidth=1, title='SuperTrend 2')
    fill(plot1, plot2, color=color.new(color.aqua, 90), title='Cloud')
    crossover_1 = ta.crossover(close, st_line2)
    long = ta.crossover(close, st_line1) and close > st_line2 or (crossover_1 and close > st_line1)
    crossunder_1 = ta.crossunder(close, st_line2)
    short = ta.crossunder(close, st_line1) and close < st_line2 or (crossunder_1 and close < st_line1)
    crossover_2 = ta.crossover(close, st_line1)
    crossunder_2 = ta.crossunder(close, st_line2)
    crossover_3 = ta.crossover(close, st_line2)
    cloud = ta.crossunder(close, st_line1) and close > st_line2 or (crossover_2 and close < st_line2) or (crossunder_2 and close > st_line1) or (crossover_3 and close < st_line1)
    inLong: Series[bool] = False
    inLong = True if long else False if short else inLong[1]
    inShort: Series[bool] = False
    inShort = True if short else False if long else inShort[1]
    plotshape(cloud and (not CrossExit), title='Close', style=shape.xcross, location=location.abovebar, color=color.new(color.red, 0), size=size.small)
    if long and time_cond and (not inLong[1] and CrossExit or not CrossExit):
        strategy.entry('long', strategy.long)
    if short and time_cond and (not inShort[1] and CrossExit or not CrossExit):
        strategy.entry('short', strategy.short)
    if not CrossExit and cloud:
        strategy.close('long')
    if not CrossExit and cloud:
        strategy.close('short')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
