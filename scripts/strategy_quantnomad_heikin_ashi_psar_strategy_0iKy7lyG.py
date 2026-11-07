"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, high, input, low, math, na, nz, open, plot, plotcandle,
    script, strategy, time, timestamp
)
from pynecore.types import Series


@script.strategy('QuantNomad - Heikin-Ashi PSAR Strategy', shorttitle='HA-PSAR[QN]', overlay=False, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    start=input(0.02, title='PSAR Start'),
    increment=input(0.02, title='PSAR Increment'),
    maximum=input(0.2, title='PSAR Max'),
    start_year=input(2018, 'Start Year'),
    start_month=input(1, 'Start Month'),
    start_day=input(1, 'Start Day'),
    end_year=input(2100, 'End Year'),
    end_month=input(1, 'End Month'),
    end_day=input(1, 'End Day')
):
    date_start = timestamp(start_year, start_month, start_day, 0, 0)
    date_end = timestamp(end_year, end_month, end_day, 0, 0)
    time_cond = time >= date_start and time <= date_end
    haopen: Series[float] = 0.0
    haclose: Series = (open + high + low + close) / 4
    haopen = (open + close) / 2 if na(haopen[1]) else (haopen[1] + haclose[1]) / 2
    hahigh: Series = math.max(high, math.max(haopen, haclose))
    halow: Series = math.min(low, math.min(haopen, haclose))
    hacolor = color.green if haclose > haopen else color.red
    psar: Series[float] = 0.0
    af: Series[float] = 0.0
    trend_dir: Series[int] = 0
    ep: Series[float] = 0.0
    trend_bars: Series[int] = 0
    sar_long_to_short = trend_dir[1] == 1 and haclose <= psar[1]
    sar_short_to_long = trend_dir[1] == -1 and haclose >= psar[1]
    trend_change = na(psar[2]) or sar_long_to_short or sar_short_to_long
    trend_dir = 1 if na(psar[2]) and haclose[1] > haopen[1] else -1 if na(psar[2]) and haclose[1] <= haopen[1] else -1 if sar_long_to_short else 1 if sar_short_to_long else nz(trend_dir[1])
    trend_bars = -1 if sar_long_to_short else 1 if sar_short_to_long else nz(trend_bars[1]) + 1 if trend_dir == 1 else nz(trend_bars[1]) - 1 if trend_dir == -1 else nz(trend_bars[1])
    af = start if trend_change else math.min(maximum, af[1] + increment) if trend_dir == 1 and hahigh > ep[1] or (trend_dir == -1 and low < ep[1]) else af[1]
    ep = hahigh if trend_change and trend_dir == 1 else halow if trend_change and trend_dir == -1 else math.max(ep[1], hahigh) if trend_dir == 1 else math.min(ep[1], halow)
    psar = halow[1] if na(psar[2]) and haclose[1] > haopen[1] else hahigh[1] if na(psar[2]) and haclose[1] <= haopen[1] else ep[1] if trend_change else psar[1] + af * (ep - psar[1]) if trend_dir == 1 else psar[1] - af * (psar[1] - ep)
    plotcandle(haopen, hahigh, halow, haclose, title='HA', color=hacolor)
    plot(psar, style=plot.style_cross, color=color.green if trend_dir == 1 else color.red, linewidth=2)
    if sar_short_to_long and time_cond:
        strategy.entry('long', strategy.long)
    if sar_long_to_short and time_cond:
        strategy.entry('short', strategy.short)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
