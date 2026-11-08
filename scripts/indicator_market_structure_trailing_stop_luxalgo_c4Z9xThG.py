"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    bar_index, close, color, display, fill, high, input, line, low, math, na,
    plot, script, ta
)
from pynecore.types import Persistent, PersistentSeries


@script.indicator('Market Structure Trailing Stop [LuxAlgo]', overlay=True, max_lines_count=500)
def main(
    length=input(14, 'Pivot Lookback'),
    incr=input.float(100, 'Increment Factor %', minval=0),
    resetOn=input.string('CHoCH', 'Reset Stop On', options=('CHoCH', 'All')),
    showMS=input(True, 'Show Structures'),
    bullCss=input(color.teal, 'Bullish MS', group='Colors'),
    bearCss=input(color.red, 'Bearish MS', group='Colors'),
    retCss=input(color.new('#FF5D00'), 'Retracement', group='Colors'),
    areaTransp=input.int(80, 'Area Transparency', minval=0, maxval=100, group='Colors')
):
    ph_y: Persistent[float] = na(float)
    ph_x: Persistent[int] = na(int)
    pl_y: Persistent[float] = na(float)
    pl_x: Persistent[int] = na(int)
    top: Persistent[float] = na(float)
    btm: Persistent[float] = na(float)
    ph_cross: Persistent[bool] = False
    pl_cross: Persistent[bool] = False
    max: PersistentSeries[float] = na(float)
    min: PersistentSeries[float] = na(float)
    ts: Persistent[float] = na(float)
    os: Persistent[int] = 0
    ms: int = 0
    n = bar_index
    ph = ta.pivothigh(length, length)
    pl = ta.pivotlow(length, length)
    if cast_bool(ph):
        ph_y = ph
        ph_x = n - length
        ph_cross = False
    if cast_bool(pl):
        pl_y = pl
        pl_x = n - length
        pl_cross = False
    if close > ph_y and (not ph_cross):
        if resetOn == 'CHoCH':
            ms = 1 if os == -1 else 0
        else:
            ms = 1
        ph_cross = True
        if showMS:
            line.new(ph_x, ph_y, n, ph_y, color=bullCss, style=line.style_dashed if os == -1 else line.style_dotted)
        os = 1
        btm = low
        for i in pine_range(0, n - ph_x - 1, 1):
            btm = math.min(low[i], btm)
    if close < pl_y and (not pl_cross):
        if resetOn == 'CHoCH':
            ms = -1 if os == 1 else 0
        else:
            ms = -1
        pl_cross = True
        if showMS:
            line.new(pl_x, pl_y, n, pl_y, color=bearCss, style=line.style_dashed if os == 1 else line.style_dotted)
        os = -1
        top = high
        for i in pine_range(0, n - pl_x - 1, 1):
            top = math.max(high[i], top)
    if ms == 1:
        max = close
    elif ms == -1:
        min = close
    else:
        max = math.max(close, max)
        min = math.min(close, min)
    ts = btm if ms == 1 else top if ms == -1 else ts + (max - max[1]) * incr / 100 if os == 1 else ts + (min - min[1]) * incr / 100
    css = na if cast_bool(ms) else bullCss if os == 1 else bearCss
    plot_price = plot(close, editable=False, display=display.none)
    plot_ts = plot(ts, 'Trailing Stop', color=css)
    css_area = retCss if (close - ts) * os < 0 else css
    fill(plot_price, plot_ts, color.new(css_area, areaTransp))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
