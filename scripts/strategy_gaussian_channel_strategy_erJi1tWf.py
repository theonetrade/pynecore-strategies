"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.series import inline_series
from pynecore.lib import (
    barcolor, color, fill, hlc3, input, math, na, nz, plot, script, strategy,
    ta, time, timestamp
)
from pynecore.types import Color, PersistentSeries, Series


@script.strategy("Gaussian Channel Strategy", overlay=True, default_qty_type=strategy.percent_of_equity, default_qty_value=100)
def main(
    startDate=input.time(timestamp('1970-01-01T00:00:00'), "Start trading date (exchange time)"),
    src: Series[float] = input.source(hlc3, "Source"),
    N=input.int(4, "Poles", minval=1, maxval=9),
    per=input.int(144, "Sampling Period", minval=2),
    mult=input.float(1.414, "Filtered True Range Multiplier", minval=0),
    modeLag=input.bool(False, "Reduced Lag Mode"),
    modeFast=input.bool(False, "Fast Response Mode"),
    sigLineLong=input.string("Filter (middle)", "Long → signal line", options=("Filter (middle)", "Upper band", "Lower band")),
    sigLineShort=input.string("Filter (middle)", "Short → signal line", options=("Filter (middle)", "Upper band", "Lower band")),
    dirLong=input.string("Cross Up", "Long when price", options=("Cross Up", "Cross Down")),
    dirShort=input.string("Cross Down", "Short when price", options=("Cross Up", "Cross Down")),
    tradeLong=input.bool(True, "Enable LONG-side trades"),
    tradeShort=input.bool(True, "Enable SHORT-side trades"),
    reverseOnOpp=input.bool(True, "On opposite signal: reverse (else just exit)"),
    lookback=input.int(3, "Lookback bars for late entry", minval=0)
):
    afterStart = time >= startDate

    def f_filt9x(_a, _s, _i):
        _x = 1 - _a
        _m2 = 36 if _i == 9 else 28 if _i == 8 else 21 if _i == 7 else 15 if _i == 6 else 10 if _i == 5 else 6 if _i == 4 else 3 if _i == 3 else 1 if _i == 2 else 0
        _m3 = 84 if _i == 9 else 56 if _i == 8 else 35 if _i == 7 else 20 if _i == 6 else 10 if _i == 5 else 4 if _i == 4 else 1 if _i == 3 else 0
        _m4 = 126 if _i == 9 else 70 if _i == 8 else 35 if _i == 7 else 15 if _i == 6 else 5 if _i == 5 else 1 if _i == 4 else 0
        _m5 = 126 if _i == 9 else 56 if _i == 8 else 21 if _i == 7 else 6 if _i == 6 else 1 if _i == 5 else 0
        _m6 = 84 if _i == 9 else 28 if _i == 8 else 7 if _i == 7 else 1 if _i == 6 else 0
        _m7 = 36 if _i == 9 else 8 if _i == 8 else 1 if _i == 7 else 0
        _m8 = 9 if _i == 9 else 1 if _i == 8 else 0
        _m9 = 1 if _i == 9 else 0
        _f: PersistentSeries[float] = na(float)
        _f = math.pow(_a, _i) * nz(_s) + _i * _x * nz(_f[1]) - (_m2 * math.pow(_x, 2) * nz(_f[2]) if _i >= 2 else 0) + (_m3 * math.pow(_x, 3) * nz(_f[3]) if _i >= 3 else 0) - (_m4 * math.pow(_x, 4) * nz(_f[4]) if _i >= 4 else 0) + (_m5 * math.pow(_x, 5) * nz(_f[5]) if _i >= 5 else 0) - (_m6 * math.pow(_x, 6) * nz(_f[6]) if _i >= 6 else 0) + (_m7 * math.pow(_x, 7) * nz(_f[7]) if _i >= 7 else 0) - (_m8 * math.pow(_x, 8) * nz(_f[8]) if _i >= 8 else 0) + (_m9 * math.pow(_x, 9) * nz(_f[9]) if _i == 9 else 0)
        return _f

    def f_pole(_a, _s, _i):
        _f1 = f_filt9x(_a, _s, 1)
        _f2 = f_filt9x(_a, _s, 2) if _i >= 2 else 0.0
        _f3 = f_filt9x(_a, _s, 3) if _i >= 3 else 0.0
        _f4 = f_filt9x(_a, _s, 4) if _i >= 4 else 0.0
        _f5 = f_filt9x(_a, _s, 5) if _i >= 5 else 0.0
        _f6 = f_filt9x(_a, _s, 6) if _i >= 6 else 0.0
        _f7 = f_filt9x(_a, _s, 7) if _i >= 7 else 0.0
        _f8 = f_filt9x(_a, _s, 8) if _i >= 8 else 0.0
        _f9 = f_filt9x(_a, _s, 9) if _i == 9 else 0.0
        __block_result__ = na
        __switch__ = _i
        if __switch__ == 1:
            __block_result__ = _f1
        elif __switch__ == 2:
            __block_result__ = _f2
        elif __switch__ == 3:
            __block_result__ = _f3
        elif __switch__ == 4:
            __block_result__ = _f4
        elif __switch__ == 5:
            __block_result__ = _f5
        elif __switch__ == 6:
            __block_result__ = _f6
        elif __switch__ == 7:
            __block_result__ = _f7
        elif __switch__ == 8:
            __block_result__ = _f8
        elif __switch__ == 9:
            __block_result__ = _f9
        _fn = __block_result__
        return (_fn, _f1)

    beta = (1 - math.cos(4 * math.asin(1) / per)) / (math.pow(1.414, 2 / N) - 1)
    alpha = -beta + math.sqrt(beta * beta + 2 * beta)
    lag = (per - 1) / (2 * N)

    srcData = src + (src - src[lag]) if modeLag else src
    trData = ta.tr(True) + (ta.tr(True) - inline_series(ta.tr(True), lag)) if modeLag else ta.tr(True)

    filtN, filt1 = f_pole(alpha, srcData, N)
    filtNtr, filt1tr = f_pole(alpha, trData, N)
    filt: Series = (filtN + filt1) / 2 if modeFast else filtN
    filtTr = (filtNtr + filt1tr) / 2 if modeFast else filtNtr

    hBand = filt + filtTr * mult
    lBand = filt - filtTr * mult

    def getLine(_c):
        __block_result_1__ = na
        if _c == 'Upper band':
            __block_result_1__ = hBand
        elif _c == 'Lower band':
            __block_result_1__ = lBand
        else:
            __block_result_1__ = filt
        return __block_result_1__

    sigLine_L = getLine(sigLineLong)
    sigLine_S = getLine(sigLineShort)

    longUp = ta.crossover(src, sigLine_L)
    longDown = ta.crossunder(src, sigLine_L)
    shortUp = ta.crossover(src, sigLine_S)
    shortDown = ta.crossunder(src, sigLine_S)

    longCond = longUp or (src > sigLine_L and ta.barssince(longUp) <= lookback) if dirLong == 'Cross Up' else longDown or (src < sigLine_L and ta.barssince(longDown) <= lookback)

    shortCond = shortUp or (src > sigLine_S and ta.barssince(shortUp) <= lookback) if dirShort == 'Cross Up' else shortDown or (src < sigLine_S and ta.barssince(shortDown) <= lookback)

    if afterStart:
        if longCond:
            if strategy.position_size < 0:
                strategy.close('Short')
            if tradeLong and (strategy.position_size == 0 or (reverseOnOpp and strategy.position_size <= 0)):
                strategy.entry('Long', strategy.long)

        if shortCond:
            if strategy.position_size > 0:
                strategy.close('Long')
            if tradeShort and (strategy.position_size == 0 or (reverseOnOpp and strategy.position_size >= 0)):
                strategy.entry('Short', strategy.short)

    upCol = color.rgb(0, 195, 255)
    upDarkCol: Color = color.new('#092AE4')
    dnCol = color.rgb(214, 10, 255)
    dnDarkCol = color.rgb(135, 0, 153)
    fCol = upCol if filt > filt[1] else dnCol if filt < filt[1] else color.gray
    barCol = upCol if src > src[1] and src > filt and (src < hBand) else color.new(upCol, 20) if src > src[1] and src >= hBand else upDarkCol if src <= src[1] and src > filt else dnCol if src < src[1] and src < filt and (src > lBand) else color.new(dnCol, 20) if src < src[1] and src <= lBand else dnDarkCol if src >= src[1] and src < filt else color.gray

    plot(filt, 'Filter', color=fCol, linewidth=3)
    hP = plot(hBand, 'Filtered TR High', color=fCol)
    lP = plot(lBand, 'Filtered TR Low', color=fCol)
    fill(hP, lP, color=color.new(fCol, 80))
    barcolor(barCol)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
