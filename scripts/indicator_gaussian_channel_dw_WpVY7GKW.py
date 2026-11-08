"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.series import inline_series
from pynecore.lib import barcolor, color, fill, hlc3, input, math, na, nz, plot, script, ta
from pynecore.types import Color, Series


@script.indicator(title='Gaussian Channel [DW]', shorttitle='GC [DW]', overlay=True, na_bool=True)
def main(
    src: Series[float] = input(defval=hlc3, title='Source'),
    N=input.int(defval=4, title='Poles', minval=1, maxval=9),
    per=input.int(defval=144, title='Sampling Period', minval=2),
    mult=input.float(defval=1.414, title='Filtered True Range Multiplier', minval=0),
    modeLag=input(defval=False, title='Reduced Lag Mode'),
    modeFast=input(defval=False, title='Fast Response Mode')
):
    def f_filt9x(_a, _s, _i):
        _m2: int = 0
        _m3: int = 0
        _m4: int = 0
        _m5: int = 0
        _m6: int = 0
        _m7: int = 0
        _m8: int = 0
        _m9: int = 0
        _f: Series[float] = 0.0
        _x = 1 - _a
        _m2 = 36 if _i == 9 else 28 if _i == 8 else 21 if _i == 7 else 15 if _i == 6 else 10 if _i == 5 else 6 if _i == 4 else 3 if _i == 3 else 1 if _i == 2 else 0
        _m3 = 84 if _i == 9 else 56 if _i == 8 else 35 if _i == 7 else 20 if _i == 6 else 10 if _i == 5 else 4 if _i == 4 else 1 if _i == 3 else 0
        _m4 = 126 if _i == 9 else 70 if _i == 8 else 35 if _i == 7 else 15 if _i == 6 else 5 if _i == 5 else 1 if _i == 4 else 0
        _m5 = 126 if _i == 9 else 56 if _i == 8 else 21 if _i == 7 else 6 if _i == 6 else 1 if _i == 5 else 0
        _m6 = 84 if _i == 9 else 28 if _i == 8 else 7 if _i == 7 else 1 if _i == 6 else 0
        _m7 = 36 if _i == 9 else 8 if _i == 8 else 1 if _i == 7 else 0
        _m8 = 9 if _i == 9 else 1 if _i == 8 else 0
        _m9 = 1 if _i == 9 else 0
        _f = math.pow(_a, _i) * nz(_s) + _i * _x * nz(_f[1]) - (_m2 * math.pow(_x, 2) * nz(_f[2]) if _i >= 2 else 0) + (_m3 * math.pow(_x, 3) * nz(_f[3]) if _i >= 3 else 0) - (_m4 * math.pow(_x, 4) * nz(_f[4]) if _i >= 4 else 0) + (_m5 * math.pow(_x, 5) * nz(_f[5]) if _i >= 5 else 0) - (_m6 * math.pow(_x, 6) * nz(_f[6]) if _i >= 6 else 0) + (_m7 * math.pow(_x, 7) * nz(_f[7]) if _i >= 7 else 0) - (_m8 * math.pow(_x, 8) * nz(_f[8]) if _i >= 8 else 0) + (_m9 * math.pow(_x, 9) * nz(_f[9]) if _i == 9 else 0)
        return _f

    def f_pole(_a, _s, _i):
        _f1 = f_filt9x(_a, _s, 1)
        _f2 = f_filt9x(_a, _s, 2) if _i >= 2 else 0
        _f3 = f_filt9x(_a, _s, 3) if _i >= 3 else 0
        _f4 = f_filt9x(_a, _s, 4) if _i >= 4 else 0
        _f5 = f_filt9x(_a, _s, 5) if _i >= 5 else 0
        _f6 = f_filt9x(_a, _s, 6) if _i >= 6 else 0
        _f7 = f_filt9x(_a, _s, 7) if _i >= 2 else 0
        _f8 = f_filt9x(_a, _s, 8) if _i >= 8 else 0
        _f9 = f_filt9x(_a, _s, 9) if _i == 9 else 0
        _fn = _f1 if _i == 1 else _f2 if _i == 2 else _f3 if _i == 3 else _f4 if _i == 4 else _f5 if _i == 5 else _f6 if _i == 6 else _f7 if _i == 7 else _f8 if _i == 8 else _f9 if _i == 9 else na
        return (_fn, _f1)

    beta = (1 - math.cos(4 * math.asin(1) / per)) / (math.pow(1.414, 2 / N) - 1)
    alpha = -beta + math.sqrt(math.pow(beta, 2) + 2 * beta)
    lag = (per - 1) / (2 * N)
    srcdata = src + src - src[lag] if modeLag else src
    trdata = ta.tr(True) + ta.tr(True) - inline_series(ta.tr(True), lag) if modeLag else ta.tr(True)
    filtn, filt1 = f_pole(alpha, srcdata, N)
    filtntr, filt1tr = f_pole(alpha, trdata, N)
    filt: Series = (filtn + filt1) / 2 if modeFast else filtn
    filttr = (filtntr + filt1tr) / 2 if modeFast else filtntr
    hband = filt + filttr * mult
    lband = filt - filttr * mult
    color1: Color = color.new('#0AFF68')
    color2: Color = color.new('#00752D')
    color3: Color = color.new('#FF0A5A')
    color4: Color = color.new('#990032')
    fcolor = color.new('#0AFF68') if filt > filt[1] else color.new('#FF0A5A') if filt < filt[1] else color.new('#CCCCCC')
    barcolor__ren__ = color.new('#0AFF68') if src > src[1] and src > filt and (src < hband) else color.new('#0AFF1B') if src > src[1] and src >= hband else color.new('#00752D') if src <= src[1] and src > filt else color.new('#FF0A5A') if src < src[1] and src < filt and (src > lband) else color.new('#FF0A11') if src < src[1] and src <= lband else color.new('#990032') if src >= src[1] and src < filt else color.new('#CCCCCC')
    filtplot = plot(filt, title='Filter', color=fcolor, linewidth=3)
    hbandplot = plot(hband, title='Filtered True Range High Band', color=fcolor)
    lbandplot = plot(lband, title='Filtered True Range Low Band', color=fcolor)
    fill(hbandplot, lbandplot, title='Channel Fill', color=color.new(fcolor, 80))
    barcolor(barcolor__ren__)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
