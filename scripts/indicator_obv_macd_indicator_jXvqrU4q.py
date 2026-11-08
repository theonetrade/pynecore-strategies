"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    close, color, high, input, location, low, math, na, nz, plot, plotshape,
    script, shape, size, ta, volume
)
from pynecore.types import NA, Persistent, Series


@script.indicator('OBV MACD Indicator', overlay=False, na_bool=True)
def main(
    len10=input(1, title='OBV Length '),
    type=input.string(defval='DEMA', title='MA Type', options=('TDEMA', 'TTEMA', 'TEMA', 'DEMA', 'EMA', 'AVG', 'THMA', 'ZLEMA', 'ZLDEMA', 'ZLTEMA', 'DZLEMA', 'TZLEMA', 'LLEMA', 'NMA')),
    len=input(9, title='MA Length '),
    slow_length=input(title='MACD Slow Length', defval=26),
    len5=input(2),
    showsignal=input(False),
    piv=input(True, 'Hide pivots?'),
    xbars=input.int(50, 'period', minval=1)
):
    src1 = close
    window_len: int = 28
    v_len: int = 14
    price_spread = ta.stdev(high - low, window_len)
    v = ta.cum(math.sign(ta.change(src1)) * volume)
    smooth = ta.sma(v, v_len)
    v_spread = ta.stdev(v - smooth, window_len)
    shadow = (v - smooth) / v_spread * price_spread
    out = high + shadow if shadow > 0 else low + shadow
    obvema = ta.ema(out, len10)
    src = obvema
    showma: bool = True
    showma1: bool = False
    len1: int = 26
    showma2: bool = False
    len2: int = 52
    def nma(src, length1, length2):
        lambda__ren__ = length1 / length2
        alpha = lambda__ren__ * (length1 - 1) / (length1 - lambda__ren__)
        ma1 = ta.ema(src, length1)
        ma2 = ta.ema(ma1, length2)
        nma__0000000e__ = (1 + alpha) * ma1 - alpha * ma2
        return nma__0000000e__

    def dema(src, len):
        ma1 = ta.ema(src, len)
        ma2 = ta.ema(ma1, len)
        return 2 * ma1 - ma2

    def tema(src, len):
        ma1 = ta.ema(src, len)
        ma2 = ta.ema(ma1, len)
        ma3 = ta.ema(ma2, len)
        return 3 * (ma1 - ma2) + ma3

    def tdema(src, len):
        ma1 = dema(src, len)
        ma2 = dema(ma1, len)
        ma3 = dema(ma2, len)
        return 3 * (ma1 - ma2) + ma3

    def ttema(src, len):
        ma1 = tema(src, len)
        ma2 = tema(ma1, len)
        ma3 = tema(ma2, len)
        return 3 * (ma1 - ma2) + ma3

    def tnma(src, len):
        ma1 = nma(src, len, 3)
        ma2 = nma(ma1, len, 3)
        ma3 = nma(ma2, len, 3)
        return 3 * (ma1 - ma2) + ma3

    def hma(src, len):
        return ta.wma(2 * ta.wma(src, len / 2) - ta.wma(src, len), math.round(math.sqrt(len)))

    def thma(src, len):
        ma1 = hma(src, len)
        ma2 = hma(ma1, len)
        ma3 = hma(ma2, len)
        return 3 * (ma1 - ma2) + ma3

    def zlema(src: Series, len):
        lag = math.round((len - 1) / 2)
        zlsrc = src + src - src[lag]
        return ta.ema(zlsrc, len)

    def zldema(src: Series, len):
        lag = math.round((len - 1) / 2)
        zlsrc = src + src - src[lag]
        return dema(zlsrc, len)

    def zltema(src: Series, len):
        lag = math.round((len - 1) / 2)
        zlsrc = src + src - src[lag]
        return tema(zlsrc, len)

    def dzlema(src, len):
        ma1 = zlema(src, len)
        ma2 = zlema(ma1, len)
        return 2 * ma1 - ma2

    def tzlema(src, len):
        ma1 = zlema(src, len)
        ma2 = zlema(ma1, len)
        ma3 = zlema(ma2, len)
        return 3 * (ma1 - ma2) + ma3

    def llema(src: Series, len):
        srcnew = 0.25 * src + 0.5 * src[1] + 0.25 * src[2]
        return ta.ema(srcnew, len)

    def lltema(src: Series, len):
        srcnew = 0.25 * src + 0.5 * src[1] + 0.25 * src[2]
        return tema(srcnew, len)

    def myma(src, len):
        __block_result__ = na
        if type == 'EMA':
            __block_result__ = ta.ema(src, len)
        else:
            __block_result_1__ = na
            if type == 'DEMA':
                __block_result_1__ = dema(src, len)
            else:
                __block_result_2__ = na
                if type == 'TEMA':
                    __block_result_2__ = tema(src, len)
                else:
                    __block_result_3__ = na
                    if type == 'TDEMA':
                        __block_result_3__ = tdema(src, len)
                    else:
                        __block_result_4__ = na
                        if type == 'TTEMA':
                            __block_result_4__ = ttema(src, len)
                        else:
                            __block_result_5__ = na
                            if type == 'THMA':
                                __block_result_5__ = thma(src, len)
                            else:
                                __block_result_6__ = na
                                if type == 'ZLEMA':
                                    __block_result_6__ = zlema(src, len)
                                else:
                                    __block_result_7__ = na
                                    if type == 'ZLDEMA':
                                        __block_result_7__ = zldema(src, len)
                                    else:
                                        __block_result_8__ = na
                                        if type == 'ZLTEMA':
                                            __block_result_8__ = zltema(src, len)
                                        else:
                                            __block_result_9__ = na
                                            if type == 'DZLEMA':
                                                __block_result_9__ = dzlema(src, len)
                                            else:
                                                __block_result_10__ = na
                                                if type == 'TZLEMA':
                                                    __block_result_10__ = tzlema(src, len)
                                                else:
                                                    __block_result_11__ = na
                                                    if type == 'LLEMA':
                                                        __block_result_11__ = llema(src, len)
                                                    else:
                                                        __block_result_12__ = na
                                                        if type == 'NMA':
                                                            __block_result_12__ = nma(src, len, len1)
                                                        else:
                                                            __block_result_12__ = math.avg(ttema(src, len), tdema(src, len))
                                                        __block_result_11__ = __block_result_12__
                                                    __block_result_10__ = __block_result_11__
                                                __block_result_9__ = __block_result_10__
                                            __block_result_8__ = __block_result_9__
                                        __block_result_7__ = __block_result_8__
                                    __block_result_6__ = __block_result_7__
                                __block_result_5__ = __block_result_6__
                            __block_result_4__ = __block_result_5__
                        __block_result_3__ = __block_result_4__
                    __block_result_2__ = __block_result_3__
                __block_result_1__ = __block_result_2__
            __block_result__ = __block_result_1__
        return __block_result__

    ma = myma(src, len) if showma else na
    src12 = close
    plot(0, linewidth=3, color=color.new(color.black, 0))
    slow_ma = ta.ema(src12, slow_length)
    macd = ma - slow_ma
    src5 = macd
    offset: int = 0
    def calcSlope(src5: Series, len5):
        sumX: float = 0.0
        sumY: float = 0.0
        sumXSqr: float = 0.0
        sumXY: float = 0.0
        for i__00000079__ in pine_range(1, len5, 1):
            val = src5[len5 - i__00000079__]
            per = i__00000079__ + 1.0
            sumX = sumX + per
            sumY = sumY + val
            sumXSqr = sumXSqr + per * per
            sumXY = sumXY + val * per
        slope = (len5 * sumXY - sumX * sumY) / (len5 * sumXSqr - sumX * sumX)
        average = sumY / len5
        intercept = average - slope * sumX / len5 + slope
        return (slope, average, intercept)

    tmp: Persistent[float] = na(float)
    s, a5, i = calcSlope(src5, len5)
    tt1 = i + s * (len5 - offset)
    p: int = 1
    src15 = tt1
    b5: Series[float] = 0.0
    dev5: Series[float] = 0.0
    oc: Series[int] = 0
    n5 = ta.cum(1) - 1
    a15 = ta.cum(math.abs(src15 - nz(b5[1], src15))) / n5 * p
    b5 = src15 if src15 > nz(b5[1], src15) + a15 else src15 if src15 < nz(b5[1], src15) - a15 else nz(b5[1], src15)
    dev5 = a15 if cast_bool(ta.change(b5)) else nz(dev5[1], a15)
    oc = 1 if ta.change(b5) > 0 else -1 if ta.change(b5) < 0 else nz(oc[1])
    cs = color.blue if oc == 1 else color.red
    plot(b5, color=cs, linewidth=4)
    down = ta.change(oc) < 0
    up = ta.change(oc) > 0
    plot(tt1 if showsignal and up else na, style=plot.style_cross, color=color.new(color.blue, 0), linewidth=4, offset=-1)
    plot(tt1 if showsignal and down else na, style=plot.style_cross, color=color.new(color.red, 0), linewidth=4, offset=-1)
    upper = tt1
    lower = tt1
    shrt: bool = False
    hb = math.abs(ta.highestbars(upper, xbars))
    lb = math.abs(ta.lowestbars(lower, xbars))
    max: Series = NA(float)
    max_upper: Series = NA(float)
    min: Series = NA(float)
    min_lower: Series = NA(float)
    pivoth = NA(bool)
    pivotl = NA(bool)
    max = close if hb == 0 else close if na(max[1]) else max[1]
    max_upper = upper if hb == 0 else upper if na(max_upper[1]) else max_upper[1]
    min = close if lb == 0 else close if na(min[1]) else min[1]
    min_lower = lower if lb == 0 else lower if na(min_lower[1]) else min_lower[1]
    if close > max:
        max = close
    if upper > max_upper:
        max_upper = upper
    if close < min_lower:
        min_lower = lower
    if lower < min_lower:
        min_lower = lower
    pivoth = True if max_upper == max_upper[2] and max_upper[2] != max_upper[3] else False
    pivotl = True if min_lower == min_lower[2] and min_lower[2] != min_lower[3] else False
    plotshape(na if piv else na if shrt else max_upper + 2 if pivoth else na, location=location.absolute, style=shape.labeldown, color=color.new(color.red, 0), size=size.tiny, text='Pivot', textcolor=color.new(color.white, 0), offset=0)
    plotshape(na if piv else na if shrt else min_lower - 2 if pivotl else na, location=location.absolute, style=shape.labelup, color=color.new(color.blue, 0), size=size.tiny, text='Pivot', textcolor=color.new(color.white, 0), offset=0)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
