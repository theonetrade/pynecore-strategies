"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    alertcondition, array, barcolor, close, color, fill, input, location,
    math, na, plot, plotshape, script, shape, size, ta
)
from pynecore.types import Persistent, Series


@script.indicator(title='Range Filter - B&S Signals', shorttitle='RF - B&S Signals', overlay=True, na_bool=True)
def main(
    rng_src: Series[float] = input(defval=close, title='Swing Source'),
    rng_per=input.int(defval=20, minval=1, title='Swing Period'),
    rng_qty=input.float(defval=3.5, minval=1e-07, title='Swing Multiplier'),
    use_barcolor=input(defval=False, title='Bar Colors On/Off')
):
    def rng_size(x: Series, qty, n):
        wper = n * 2 - 1
        avrng = ta.ema(math.abs(x - x[1]), n)
        AC = ta.ema(avrng, wper) * qty
        rng_size__00000006__ = AC
        return rng_size__00000006__

    def rng_filt(x, rng_, n):
        r = rng_
        rfilt: Persistent[list[float]] = array.new_float(2, x)
        array.set(rfilt, 1, array.get(rfilt, 0))
        if x - r > array.get(rfilt, 1):
            array.set(rfilt, 0, x - r)
        if x + r < array.get(rfilt, 1):
            array.set(rfilt, 0, x + r)
        rng_filt1 = array.get(rfilt, 0)
        hi_band = rng_filt1 + r
        lo_band = rng_filt1 - r
        rng_filt__00000011__ = rng_filt1
        return (hi_band, lo_band, rng_filt__00000011__)

    filt: Series
    h_band, l_band, filt = rng_filt(rng_src, rng_size(rng_src, rng_qty, rng_per), rng_per)
    fdir: Persistent[float] = 0.0
    fdir = 1 if filt > filt[1] else -1 if filt < filt[1] else fdir
    upward = 1 if fdir == 1 else 0
    downward = 1 if fdir == -1 else 0
    longCond = rng_src > filt and rng_src > rng_src[1] and (upward > 0) or (rng_src > filt and rng_src < rng_src[1] and (upward > 0))
    shortCond = rng_src < filt and rng_src < rng_src[1] and (downward > 0) or (rng_src < filt and rng_src > rng_src[1] and (downward > 0))
    CondIni: Series[int] = 0
    CondIni = 1 if longCond else -1 if shortCond else CondIni[1]
    longCondition = longCond and CondIni[1] == -1
    shortCondition = shortCond and CondIni[1] == 1
    filt_color = color.new('#05FF9B') if cast_bool(upward) else color.new('#FF0583') if cast_bool(downward) else color.new('#CCCCCC')
    bar_color = (color.new('#05FF9B') if rng_src > rng_src[1] else color.new('#00B36B')) if cast_bool(upward) and rng_src > filt else (color.new('#FF0583') if rng_src < rng_src[1] else color.new('#B8005D')) if cast_bool(downward) and rng_src < filt else color.new('#CCCCCC')
    filt_plot = plot(filt, color=filt_color, linewidth=3, title='Filter')
    h_band_plot = plot(h_band, color=color.new(color.new('#05FF9B'), 100), title='High Band')
    l_band_plot = plot(l_band, color=color.new(color.new('#FF0583'), 100), title='Low Band')
    fill(h_band_plot, filt_plot, color=color.new(color.new('#00B36B'), 92), title='High Band Fill')
    fill(l_band_plot, filt_plot, color=color.new(color.new('#B8005D'), 92), title='Low Band Fill')
    barcolor(bar_color if use_barcolor else na)
    plotshape(longCondition, title='Buy Signal', text='BUY', textcolor=color.white, style=shape.labelup, size=size.normal, location=location.belowbar, color=color.new(color.green, 0))
    plotshape(shortCondition, title='Sell Signal', text='SELL', textcolor=color.white, style=shape.labeldown, size=size.normal, location=location.abovebar, color=color.new(color.red, 0))
    alertcondition(longCondition, title='Buy Alert', message='BUY')
    alertcondition(shortCondition, title='Sell Alert', message='SELL')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
