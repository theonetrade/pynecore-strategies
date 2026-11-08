"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from dataclasses import field as _dataclass_field
from pynecore.core.pine_method import method, method_call
from pynecore.core.pine_udt import udt
from pynecore.core.series import inline_series
from pynecore.lib import (
    alert, alertcondition, barcolor, chart, close, color, display, fill,
    high, hline, input, location, low, math, na, nz, open, plot, plotcandle, plotshape, script,
    shape, size, ta
)
from pynecore.types import Color, Persistent, PersistentSeries, Series


@udt
class bar:
    o: float = na(float)
    h: float = na(float)
    l: float = na(float)
    c: float = na(float)


@udt
class osc:
    b: 'bar' = _dataclass_field(default_factory=lambda: na(bar))
    s: float = na(float)
    h: float = na(float)


@udt
class alerts:
    s: bool = na(bool)
    b: bool = na(bool)
    u: bool = na(bool)
    d: bool = na(bool)
    p: bool = na(bool)
    n: bool = na(bool)
    x: bool = na(bool)
    y: bool = na(bool)


@udt
class prompt:
    s: str = ''
    c: bool = False


gm: str = 'MACD Settings'
gu: str = 'UI Options'
colup: Color = color.new('#00BCD4')
coldn: Color = color.new('#FC1F1F')
colhu: Color = color.new('#8AC3F5')
colhd: Color = color.new('#FFA7B6')


@script.indicator('Standardized MACD Heikin-Ashi Transformed', '[Ʌ] - 𝗦𝘁. 𝗠𝗔𝗖𝗗 𝗛-𝗔', False, na_bool=True)
def main(
    src__global__=input.string('close', 'Source', options=('open', 'high', 'low', 'close', 'hl2', 'hlc3', 'ohlc4', 'hlcc4'), group=gm),
    fast=input.int(12, 'Fast Length', group=gm),
    slow=input.int(26, 'Slow Length', group=gm),
    sigb=input.bool(True, 'Signal', inline='1', group=gm),
    sigs=input.string('close', 'Source', options=('open', 'high', 'low', 'close', 'hl2', 'hlc3', 'ohlc4', 'hlcc4'), inline='1', group=gm),
    sigl=input.int(9, 'Length', inline='1', group=gm),
    mode=input.string('Hybrid', 'Display Mode', options=('Hybrid', 'MACD', 'Histogram'), group=gu),
    revs=input.bool(True, '', inline='0', group=gu),
    revt=input.int(100, 'Reversion Threshold', options=(100, 150), inline='0', group=gu),
    colb=input.string('None', 'Bar Coloring', options=('None', 'MidLine', 'Candles', 'Sig Cross', 'Extremities', 'Reversions'), group=gu),
    hol=input.bool(True, 'Hollow Candles', group=gu)
):
    @method
    def notify(p: prompt):
        __block_result__ = na
        if p.c:
            __block_result__ = alert(p.s, alert.freq_once_per_bar_close)
        return __block_result__

    @method
    def any(a: alerts):
        __block_result_1__ = na
        if a.s:
            __block_result_1__ = 'OB Signal'
        elif a.b:
            __block_result_1__ = 'OS Signal'
        elif a.u:
            __block_result_1__ = 'Bullish Trend'
        elif a.d:
            __block_result_1__ = 'Bearish Trend'
        elif a.p:
            __block_result_1__ = 'Heikin-Ashi Uptrend  '
        elif a.n:
            __block_result_1__ = 'Heikin-Ashi Downtrend'
        elif a.x:
            __block_result_1__ = 'MACD Bullish Cross'
        elif a.y:
            __block_result_1__ = 'MACD Bearish Cross'
        else:
            __block_result_1__ = na
        s: str = __block_result_1__
        return prompt(s, not na(s))

    @method
    def src(b: bar, src__00000023__: str):
        __block_result_2__ = na
        __switch__ = src__00000023__
        if __switch__ == 'open':
            __block_result_2__ = b.o
        elif __switch__ == 'high':
            __block_result_2__ = b.h
        elif __switch__ == 'low':
            __block_result_2__ = b.l
        elif __switch__ == 'close':
            __block_result_2__ = b.c
        elif __switch__ == 'oc2':
            __block_result_2__ = math.avg(b.o, b.c)
        elif __switch__ == 'hl2':
            __block_result_2__ = math.avg(b.h, b.l)
        elif __switch__ == 'hlc3':
            __block_result_2__ = math.avg(b.h, b.l, b.c)
        elif __switch__ == 'ohlc4':
            __block_result_2__ = math.avg(b.o, b.h, b.l, b.c)
        elif __switch__ == 'hlcc4':
            __block_result_2__ = math.avg(b.h, b.l, b.c, b.c)
        x: float = __block_result_2__
        return x

    @method
    def ha(b: bar, p: bool = True):
        x: PersistentSeries[bar] = bar()
        x.c = src(b, 'ohlc4')
        field_0: Series[float] = x.o
        x = bar(src(b, 'oc2') if na(field_0[1]) else nz(inline_series(src(x, 'oc2'), 1)), math.max(b.h, math.max(x.o, x.c)), math.min(b.l, math.min(x.o, x.c)), x.c)
        return x if p else b

    @method
    def stmc(b: bar, src__00000041__: str, flen: int, slen: int, sig: str, clen: int):
        x: Series[float] = (ta.ema(src(b, src__00000041__), flen) - ta.ema(src(b, src__00000041__), slen)) / ta.ema(b.h - b.l, slen) * 100
        z: bar = method_call(ha, bar(x[1], math.max(x, x[1]), math.min(x, x[1]), x))
        s: float = ta.ema(src(z, sig), clen)
        return osc(z, s, z.c - s)

    b: bar = bar(open, high, low, close)
    o: osc = stmc(b, src__global__, fast, slow, sigs, sigl)
    colnt: Persistent[Color] = chart.fg_color
    field_1: Series[float] = o.h
    field_2: Series[float] = o.h
    colh: Color = (color.new(colhu, 20) if o.h > field_1[1] else color.new(colhu, 30)) if o.h > 0 else color.new(colhd, 20) if o.h > field_2[1] else color.new(colhd, 30)
    __block_result_3__ = na
    if o.b.c > o.b.o:
        __block_result_3__ = colup
    elif o.b.c < o.b.o:
        __block_result_3__ = coldn
    haColor: Color = __block_result_3__
    m = hline(0, 'Mid Line', chart.fg_color, hline.style_solid)
    min = hline(-200 if mode != 'Histogram' else -100, display=display.none)
    ll = hline(-150 if mode != 'Histogram' else -75, display=display.none)
    hl = hline(-100 if mode != 'Histogram' else -50, display=display.none)
    max = hline(200 if mode != 'Histogram' else 100, display=display.none)
    hh = hline(150 if mode != 'Histogram' else 75, display=display.none)
    lh = hline(100 if mode != 'Histogram' else 50, display=display.none)
    h = plot(o.s if mode != 'Histogram' and sigb else na, 'Signal', colnt)
    mc = plot(o.h if mode != 'MACD' else na, 'H', colh, 1, plot.style_columns)
    fill(lh, hh, color.new(coldn, 90))
    fill(hh, max, color.new(coldn, 80))
    fill(ll, hl, color.new(colup, 80))
    fill(ll, min, color.new(colup, 80))
    plotcandle(o.b.o if mode != 'Histogram' else na, o.b.h if mode != 'Histogram' else na, o.b.l if mode != 'Histogram' else na, o.b.c if mode != 'Histogram' else na, '𝗠𝗔𝗖𝗗', (na if o.b.c > o.b.o else haColor) if hol else haColor, haColor, bordercolor=haColor)
    a: alerts = alerts(ta.crossunder(o.b.c, o.b.o) and o.b.h > revt, ta.crossover(o.b.c, o.b.o) and o.b.l < -revt, ta.crossover(o.b.c, 0), ta.crossunder(o.b.c, 0), ta.crossunder(o.b.c, o.b.o) and (not o.b.h > revt), ta.crossover(o.b.c, o.b.o) and (not o.b.l < -revt), ta.crossover(o.b.c, o.s), ta.crossunder(o.b.c, o.s))
    plotshape(((o.b.h + 40 if a.s else na) if revs else na) if mode != 'Histogram' else na, 'OB', shape.triangledown, location.absolute, coldn, size=size.tiny)
    plotshape(((o.b.l - 40 if a.b else na) if revs else na) if mode != 'Histogram' else na, 'OS', shape.triangleup, location.absolute, colup, size=size.tiny)
    alertcondition(a.s, 'Overbought', 'OB Signal')
    alertcondition(a.b, 'Oversold  ', 'OS Signal')
    alertcondition(a.u, 'Midline Crossover ', 'Bullish Trend')
    alertcondition(a.d, 'Midline Crossunder', 'Bearish Trend')
    alertcondition(a.p, 'Positive Heikin-Ashi', 'Heikin-Ashi Uptrend  ')
    alertcondition(a.n, 'Negative Heikin-Ashi', 'Heikin-Ashi Downtrend')
    alertcondition(a.x, 'MACD Bull Cross', 'MACD Bullish Cross')
    alertcondition(a.y, 'MACD Bear Cross', 'MACD Bearish Cross')
    method_call(notify, any(a))
    __block_result_4__ = na
    __switch__ = colb
    if __switch__ == 'MidLine':
        __block_result_4__ = colup if o.b.c > 0 else coldn
    elif __switch__ == 'Candles':
        __block_result_4__ = colup if o.b.c > o.b.o else coldn
    elif __switch__ == 'Sig Cross':
        __block_result_4__ = coldn if o.s > o.b.c else colup
    elif __switch__ == 'Extremities':
        __block_result_4__ = coldn if o.b.c > revt else colup if o.b.c < -revt else color.new(colnt, 25)
    elif __switch__ == 'Reversions':
        __block_result_4__ = coldn if a.b else colup if a.s else color.new(colnt, 25)
    elif __switch__ == 'None':
        __block_result_4__ = na
    col: Color = __block_result_4__
    barcolor(col)
    plot(o.b.o, 'open', editable=False, display=display.none)
    plot(o.b.h, 'high', editable=False, display=display.none)
    plot(o.b.l, 'low', editable=False, display=display.none)
    plot(o.b.c, 'close', editable=False, display=display.none)
    plot(src(o.b, 'hl2'), 'hl2', editable=False, display=display.none)
    plot(src(o.b, 'hlc3'), 'hlc3', editable=False, display=display.none)
    plot(src(o.b, 'ohlc4'), 'ohlc4', editable=False, display=display.none)
    plot(src(o.b, 'hlcc4'), 'hlcc4', editable=False, display=display.none)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
