"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    alertcondition, bar_index, close, color, extend, input, line, location,
    math, na, plot, plotshape, request, script, shape, syminfo, ta, time, timeframe, timestamp,
    xloc
)
from pynecore.types import Line, PersistentSeries, Series


@script.indicator('Linear Regression ++ [Dev Lucem]', 'Lin Reg ++ [DL]', overlay=True)
def main(
    mtf_val=input.timeframe('', 'Resolution', inline='config', group='Algorithm Config'),
    source: Series[float] = input.source(close, inline='config', group='Algorithm Config'),
    length=input.int(100, minval=1, inline='config1', group='Algorithm Config'),
    dev=input(2.0, 'Deviation', inline='config1', group='Algorithm Config'),
    offset=input.int(0, minval=0, inline='config2', group='Algorithm Config'),
    smoothing=input.int(1, minval=1, inline='config2', group='Algorithm Config'),
    line_thick=input.int(4, 'S&R Size', minval=1, maxval=4, inline='levels', group='Display Config'),
    show_last=input.bool(True, 'Hide Old Signals', group='Display Config'),
    p=input.color(color.lime, 'Up', inline='colors', group='Display Config'),
    q=input.color(color.red, 'Down', inline='colors', group='Display Config'),
    displacement=input.bool(False, 'Show Displacement'),
    goto=input.time(timestamp('20 Jul 2050 00:00 +0300'), 'End Of Calculating')
):
    def data(x):
        return ta.sma(request.security(syminfo.tickerid, mtf_val if mtf_val != '' else timeframe.period, x), smoothing)

    linreg: Series = data(ta.linreg(source, length, offset))
    linreg_p = data(ta.linreg(source, length, offset + 1))
    plot(linreg, 'Regression Line', p if linreg > linreg[1] else q, editable=True)
    x = bar_index
    slope = linreg - linreg_p
    intercept = linreg - x * slope
    deviationSum: float = 0.0
    for i in pine_range(0, length - 1, 1):
        deviationSum = deviationSum + math.pow(source[i] - (slope * (x - i) + intercept), 2)
    deviation = math.sqrt(deviationSum / length)
    x1 = x - length
    x2 = x
    y1 = slope * (x - length) + intercept
    y2 = linreg
    b: PersistentSeries[Line] = na(Line)
    dp: PersistentSeries[Line] = na(Line)
    dm: PersistentSeries[Line] = na(Line)
    updating = goto >= time
    if updating:
        b = line.new(x1, y1, x2, y2, xloc.bar_index, extend.right, color.aqua, width=line_thick)
        if not displacement:
            line.delete(b[1])
        dp = line.new(x1, deviation * dev + y1, x2, deviation * dev + y2, xloc.bar_index, extend.right, q, width=line_thick)
        if not displacement:
            line.delete(dp[1])
        dm = line.new(x1, -deviation * dev + y1, x2, -deviation * dev + y2, xloc.bar_index, extend.right, p, width=line_thick)
        if not displacement:
            line.delete(dm[1])
    dm_current = -deviation * dev + y2
    dp_current = deviation * dev + y2
    buy = ta.crossunder(close, dm_current)
    sell = ta.crossover(close, dp_current)
    alertcondition(buy, 'Buy Lin Reg', 'Crossing On the Lower Regression Channel')
    alertcondition(sell, 'Sell Lin Reg', 'Crossing On the Higher Regression Channel')
    plotshape(buy, 'BUY', shape.labelup, location.belowbar, color.new(color.lime, 0), text='BUY', textcolor=color.new(color.black, 0), show_last=99999999 if not show_last else length)
    plotshape(sell, 'SELL', shape.labeldown, location.abovebar, color.new(color.red, 0), text='SELL', textcolor=color.new(color.white, 0), show_last=99999999 if not show_last else length)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
