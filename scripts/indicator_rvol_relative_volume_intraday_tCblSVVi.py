"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    array, bar_index, barmerge, close, color, extend, hline, input,
    last_bar_index, line, math, na, open, plot, request, runtime, script, syminfo, ta, time,
    timeframe, volume
)
from pynecore.types import Persistent, Series

tooltip1: str = 'The more recent the data is, the more relevant it is.  Longer period baselines have lower volumes. This creates too much noise when we generate our results.'


@script.indicator('RVOL Relative Volume - Intraday', 'RVOL', max_lines_count=500, precision=2)
def main(
    period=input.int(defval=5, title='Number of Days', minval=1, maxval=55, tooltip=tooltip1),
    dls=input.int(defval=0, title='Daylight saving on last weekend', tooltip='Please enter ±1 if Daylight saving last weekend, Otherwise please keep it 0')
):
    if not timeframe.isintraday or timeframe.isseconds:
        runtime.error('Chart time frame must be less than 1 Day and greater/equal 1 minute')
    hline(0.0, linestyle=hline.style_solid)
    hline(0.5, linestyle=hline.style_dotted)
    hline(1.0, linestyle=hline.style_dashed)
    hline(1.5, linestyle=hline.style_dotted)
    hline(2.0, linestyle=hline.style_dashed)
    lbi = request.security(syminfo.tickerid, 'W', last_bar_index)
    cbi = request.security(syminfo.tickerid, 'W', bar_index, lookahead=barmerge.lookahead_on)
    hour_: int = math.floor(time / 3600000) % 24 + (dls if lbi == cbi else 0)
    minute_: int = math.floor(time / 60000) % 60
    rvols: Persistent[list[float]] = array.new_float(24 * 60 * 2 * (period + 1), 0)
    newday: bool = ta.change(time('D')) != 0
    plus24: Persistent[int] = 0
    if newday:
        plus24 = 0
        for x in pine_range(1, 2880, 1):
            array.shift(rvols)
            array.push(rvols, 0)
    ctime_: Series[int] = hour_ * 60 + minute_
    if ctime_ < ctime_[1] and (not newday):
        plus24 = 1440
    ctime: Series[int] = ctime_ + plus24
    if newday:
        line.new(x1=bar_index, y1=0, x2=bar_index, y2=1, color=color.gray, style=line.style_dashed, extend=extend.right)
    array.set(rvols, period * 2880 + ctime, volume if newday else array.get(rvols, period * 2880 + ctime[1]) + volume)
    def relativeVolume():
        hvol: float = 0
        for x in pine_range(0, period - 1, 1):
            svol = array.get(rvols, x * 2880 + ctime)
            if svol == 0:
                for y in pine_range(x * 2880 + ctime, x * 2880, 1):
                    svol = array.get(rvols, y)
                    if svol != 0:
                        break
            hvol = hvol + svol / period
        cvol = array.get(rvols, period * 2880 + ctime)
        rvol = 0 if hvol == 0 else cvol / hvol
        return rvol

    RVOL = relativeVolume()
    plot(RVOL, style=plot.style_columns, color=color.rgb(0, math.max(math.min(RVOL * 130, 255), 130), 0, 0) if close >= open else color.rgb(math.max(math.min(RVOL * 130, 255), 130), 0, 0, 0))
    plot(0, color=color.blue if na(volume) else color.red)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
