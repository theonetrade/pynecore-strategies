"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    array, barcolor, close, color, display, fill, high, input, low, math, na,
    plot, script, syminfo, ta
)
from pynecore.types import Persistent, Series


@script.indicator(title='Range Filter [DW]', shorttitle='RF [DW]', overlay=True, na_bool=True)
def main(
    f_type=input.string(defval='Type 1', options=('Type 1', 'Type 2'), title='Filter Type'),
    mov_src=input.string(defval='Close', options=('Wicks', 'Close'), title='Movement Source'),
    rng_qty=input.float(defval=2.618, minval=1e-07, title='Range Size'),
    rng_scale=input.string(defval='Average Change', options=('Points', 'Pips', 'Ticks', '% of Price', 'ATR', 'Average Change', 'Standard Deviation', 'Absolute'), title='Range Scale'),
    rng_per=input.int(defval=14, minval=1, title='Range Period (for ATR, Average Change, and Standard Deviation)'),
    smooth_range=input(defval=True, title='Smooth Range'),
    smooth_per=input.int(defval=27, minval=1, title='Smoothing Period'),
    av_vals=input(defval=False, title='Average Filter Changes'),
    av_samples=input.int(defval=2, minval=1, title='Number Of Changes To Average')
):
    def Cond_EMA(x, cond, n):
        val: Persistent[list[float]] = array.new_float(0)
        ema_val: Persistent[list[float]] = array.new_float(1)
        if cond:
            array.push(val, x)
            if array.size(val) > 1:
                array.remove(val, 0)
            if na(array.get(ema_val, 0)):
                array.fill(ema_val, array.get(val, 0))
            array.set(ema_val, 0, (array.get(val, 0) - array.get(ema_val, 0)) * (2 / (n + 1)) + array.get(ema_val, 0))
        EMA = array.get(ema_val, 0)
        return EMA

    def Cond_SMA(x, cond, n):
        vals: Persistent[list[float]] = array.new_float(0)
        if cond:
            array.push(vals, x)
            if array.size(vals) > n:
                array.remove(vals, 0)
        SMA = array.avg(vals)
        return SMA

    def Stdev(x, n):
        return math.sqrt(Cond_SMA(math.pow(x, 2), 1, n) - math.pow(Cond_SMA(x, 1, n), 2))

    def rng_size(x: Series, scale__ren__, qty, n):
        ATR = Cond_EMA(ta.tr(True), 1, n)
        AC = Cond_EMA(math.abs(x - x[1]), 1, n)
        SD = Stdev(x, n)
        rng_size__00000028__ = qty * 0.0001 if scale__ren__ == 'Pips' else qty * syminfo.pointvalue if scale__ren__ == 'Points' else close * qty / 100 if scale__ren__ == '% of Price' else qty * ATR if scale__ren__ == 'ATR' else qty * AC if scale__ren__ == 'Average Change' else qty * SD if scale__ren__ == 'Standard Deviation' else qty * syminfo.mintick if scale__ren__ == 'Ticks' else qty
        return rng_size__00000028__

    def rng_filt(h, l, rng_, n, type, smooth, sn, av_rf, av_n):
        rng_smooth = Cond_EMA(rng_, 1, sn)
        r = rng_smooth if smooth else rng_
        rfilt: Persistent[list[float]] = array.new_float(2, (h + l) / 2)
        array.set(rfilt, 1, array.get(rfilt, 0))
        if type == 'Type 1':
            if h - r > array.get(rfilt, 1):
                array.set(rfilt, 0, h - r)
            if l + r < array.get(rfilt, 1):
                array.set(rfilt, 0, l + r)
        if type == 'Type 2':
            if h >= array.get(rfilt, 1) + r:
                array.set(rfilt, 0, array.get(rfilt, 1) + math.floor(math.abs(h - array.get(rfilt, 1)) / r) * r)
            if l <= array.get(rfilt, 1) - r:
                array.set(rfilt, 0, array.get(rfilt, 1) - math.floor(math.abs(l - array.get(rfilt, 1)) / r) * r)
        rng_filt1: Series = array.get(rfilt, 0)
        hi_band1 = rng_filt1 + r
        lo_band1 = rng_filt1 - r
        rng_filt2 = Cond_EMA(rng_filt1, rng_filt1 != rng_filt1[1], av_n)
        hi_band2 = Cond_EMA(hi_band1, rng_filt1 != rng_filt1[1], av_n)
        lo_band2 = Cond_EMA(lo_band1, rng_filt1 != rng_filt1[1], av_n)
        rng_filt__0000004a__ = rng_filt2 if av_rf else rng_filt1
        hi_band = hi_band2 if av_rf else hi_band1
        lo_band = lo_band2 if av_rf else lo_band1
        return (hi_band, lo_band, rng_filt__0000004a__)

    h_val = high if mov_src == 'Wicks' else close
    l_val = low if mov_src == 'Wicks' else close
    filt: Series
    h_band, l_band, filt = rng_filt(h_val, l_val, rng_size((h_val + l_val) / 2, rng_scale, rng_qty, rng_per), rng_per, f_type, smooth_range, smooth_per, av_vals, av_samples)
    fdir: Persistent[float] = 0.0
    fdir = 1 if filt > filt[1] else -1 if filt < filt[1] else fdir
    upward = 1 if fdir == 1 else 0
    downward = 1 if fdir == -1 else 0
    filt_color = color.new('#05FF9B') if cast_bool(upward) else color.new('#FF0583') if cast_bool(downward) else color.new('#CCCCCC')
    bar_color = (color.new('#05FF9B') if close > close[1] else color.new('#00B36B')) if cast_bool(upward) and close > filt else (color.new('#FF0583') if close < close[1] else color.new('#B8005D')) if cast_bool(downward) and close < filt else color.new('#CCCCCC')
    filt_plot = plot(filt, color=filt_color, linewidth=3, title='Filter')
    h_band_plot = plot(h_band, color=color.new(color.new('#05FF9B'), 100), title='High Band')
    l_band_plot = plot(l_band, color=color.new(color.new('#FF0583'), 100), title='Low Band')
    fill(h_band_plot, filt_plot, color=color.new(color.new('#00B36B'), 85), title='High Band Fill')
    fill(l_band_plot, filt_plot, color=color.new(color.new('#B8005D'), 85), title='Low Band Fill')
    barcolor(bar_color)
    plot(fdir, editable=False, display=display.none, title='External Output - Trend Signal')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)