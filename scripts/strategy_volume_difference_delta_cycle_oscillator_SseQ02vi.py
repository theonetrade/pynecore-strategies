"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bgcolor, close, color, hline, input, math, na, nz, plot, script,
    strategy, syminfo, ta, time, timestamp, volume
)
from pynecore.types import Persistent, Series


@script.strategy('Volume Difference Delta Cycle Oscillator', 'VDDC Osc', default_qty_type=strategy.percent_of_equity, default_qty_value=100, max_bars_back=5000, margin_long=0, margin_short=0, initial_capital=1000000, close_by_id=True)
def main(
    startDate=input.int(title='Start Date', defval=1, minval=1, maxval=31),
    startMonth=input.int(title='Start Month', defval=1, minval=1, maxval=12),
    startYear=input.int(title='Start Year', defval=2010, minval=1800, maxval=2100),
    endDate=input.int(title='End Date', defval=31, minval=1, maxval=31),
    endMonth=input.int(title='End Month', defval=12, minval=1, maxval=12),
    endYear=input.int(title='End Year', defval=2021, minval=1800, maxval=2100),
    __input_6__=input(2.0, title='Long Stop Loss %'),
    __input_7__=input(4.0, title='Long Take Profit %'),
    __input_8__=input(2.0, title='Short Stop Loss %'),
    __input_9__=input(4.0, title='Short Take Profit %'),
    length=input.int(20, minval=1, title='Volume Bands Length'),
    mult=input.float(2.0, minval=0.001, maxval=50, title='Volume Bands StdDev'),
    l1=input.int(20, minval=1, title='Bollinger Bands Length'),
    mult1=input.float(2.0, minval=0.001, maxval=50, title='Bollinger Bands StdDev'),
    __input_14__=input(2, title='Hist Smoothing Factor #1'),
    __input_15__=input(2, title='Hist Smoothing Factor #2'),
    __input_16__=input(2, title='Hist Smoothing Factor #3'),
    oversold=input(-0.1),
    overbought=input(0.4)
):
    def normalize(_src, _min, _max):
        _historicMin: Persistent[float] = 100000000000.0
        _historicMax: Persistent = -100000000000.0
        _historicMin = math.min(nz(_src, _historicMin), _historicMin)
        _historicMax = math.max(nz(_src, _historicMax), _historicMax)
        return _min + (_max - _min) * (_src - _historicMin) / math.max(_historicMax - _historicMin, 1e-09)

    inDateRange = time >= timestamp(syminfo.timezone, startYear, startMonth, startDate, 0, 0) and time < timestamp(syminfo.timezone, endYear, endMonth, endDate, 0, 0)
    l_sl_inp = __input_6__ / 100
    l_tp_inp = __input_7__ / 100
    l_stop_level = strategy.position_avg_price * (1 - l_sl_inp)
    l_take_level = strategy.position_avg_price * (1 + l_tp_inp)
    s_sl_inp = __input_8__ / 100
    s_tp_inp = __input_9__ / 100
    s_stop_level = strategy.position_avg_price * (1 + s_sl_inp)
    s_take_level = strategy.position_avg_price * (1 - s_tp_inp)
    src = close
    change_src: float = ta.change(src)
    i_obv: float = ta.cum(volume if change_src > 0 else -volume if change_src < 0 else 0 * volume)
    i_pvt: float = ta.pvt
    result: float = ta.change(i_obv - i_pvt)
    nresult: float = ta.ema(normalize(result, -1, 1), 20)
    basis = ta.ema(nresult, length)
    dev = mult * ta.stdev(nresult, length)
    upper = basis + dev
    lower = basis - dev
    bbr = (nresult - lower) / (upper - lower)
    src2 = close
    basis1 = ta.sma(src2, l1)
    dev1 = mult1 * ta.stdev(src2, l1)
    upper1 = basis1 + dev1
    lower1 = basis1 - dev1
    bbr1 = (src - lower1) / (upper1 - lower1)
    hist: Series = ta.ema(ta.ema(ta.ema(bbr1 - bbr, __input_14__), __input_15__), __input_16__)
    hline(oversold, linewidth=2, color=color.new(color.new('#81C784'), 62))
    hline(overbought, linewidth=2, color=color.new(color.new('#C2185B'), 38))
    short = hist > overbought
    long = hist < oversold
    histColor = (color.new('#26A69A') if hist[1] < hist else color.new('#B2DFDB')) if hist >= 0 else color.new('#FFCDD2') if hist[1] < hist else color.new('#EF5350')
    plot(hist, title='Histogram', style=plot.style_columns, color=color.new(histColor, 0))
    CrossBgColor = color.new(color.new('#81C784'), 62) if long else color.new(color.new('#C2185B'), 38) if short else na
    bgcolor(color.new(CrossBgColor, 90))
    if inDateRange:
        if long:
            strategy.entry('long', strategy.long, stop=l_stop_level, limit=l_take_level)
    if inDateRange and strategy.position_size > 0:
        if short:
            strategy.close_all()
    if inDateRange:
        if short:
            strategy.entry('short', strategy.short, stop=s_stop_level, limit=s_take_level)
    if inDateRange and strategy.position_size < 0:
        if long:
            strategy.close_all()


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
