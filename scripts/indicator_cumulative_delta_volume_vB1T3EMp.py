"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, high, input, low, math, na, nz, open, plot, plotcandle,
    script, ta, volume
)
from pynecore.types import Series


@script.indicator('Cumulative Delta Volume', 'CDV', na_bool=True)
def main(
    linestyle=input.string(defval='Candle', title='Style', options=('Candle', 'Line')),
    hacandle=input(defval=True, title='Heikin Ashi Candles?'),
    showma1=input.bool(defval=False, title='SMA 1', inline='ma1'),
    ma1len=input.int(defval=50, title='', minval=1, inline='ma1'),
    ma1col=input.color(defval=color.lime, title='', inline='ma1'),
    showma2=input.bool(defval=False, title='SMA 2', inline='ma2'),
    ma2len=input.int(defval=200, title='', minval=1, inline='ma2'),
    ma2col=input.color(defval=color.red, title='', inline='ma2'),
    showema1=input.bool(defval=False, title='EMA 1', inline='ema1'),
    ema1len=input.int(defval=50, title='', minval=1, inline='ema1'),
    ema1col=input.color(defval=color.lime, title='', inline='ema1'),
    showema2=input.bool(defval=False, title='EMA 2', inline='ema2'),
    ema2len=input.int(defval=200, title='', minval=1, inline='ema2'),
    ema2col=input.color(defval=color.red, title='', inline='ema2'),
    colorup=input.color(defval=color.lime, title='Body', inline='bcol'),
    colordown=input.color(defval=color.red, title='', inline='bcol'),
    bcolup=input.color(defval=color.new('#74E05E'), title='Border', inline='bocol'),
    bcoldown=input.color(defval=color.new('#FFAD7D'), title='', inline='bocol'),
    wcolup=input.color(defval=color.new('#B5B5B8'), title='Wicks', inline='wcol'),
    wcoldown=input.color(defval=color.new('#B5B5B8'), title='', inline='wcol')
):
    tw = high - math.max(open, close)
    bw = math.min(open, close) - low
    body = math.abs(close - open)
    def _rate(cond):
        ret = 0.5 * (tw + bw + (2 * body if cond else 0)) / (tw + bw + body)
        ret = 0.5 if nz(ret) == 0 else ret
        return ret

    deltaup = volume * _rate(open <= close)
    deltadown = volume * _rate(open > close)
    delta = deltaup if close >= open else -deltadown
    cumdelta: Series = ta.cum(delta)
    ctl: float = na(float)
    o: float = na(float)
    h: float = na(float)
    l: float = na(float)
    c: float = na(float)
    if linestyle == 'Candle':
        o = cumdelta[1]
        h = math.max(cumdelta, cumdelta[1])
        l = math.min(cumdelta, cumdelta[1])
        c = cumdelta
    else:
        ctl = cumdelta
    plot(ctl, title='CDV Line', color=color.new(color.blue, 0), linewidth=2)
    haclose: Series[float] = na(float)
    haopen: Series[float] = na(float)
    hahigh: float = na(float)
    halow: float = na(float)
    haclose = (o + h + l + c) / 4
    haopen = (o + c) / 2 if na(haopen[1]) else (haopen[1] + haclose[1]) / 2
    hahigh = math.max(h, math.max(haopen, haclose))
    halow = math.min(l, math.min(haopen, haclose))
    c_ = haclose if hacandle else c
    o_ = haopen if hacandle else o
    h_ = hahigh if hacandle else h
    l_ = halow if hacandle else l
    plotcandle(o_, h_, l_, c_, title='CDV Candles', color=colorup if o_ <= c_ else colordown, bordercolor=bcolup if o_ <= c_ else bcoldown, wickcolor=bcolup if o_ <= c_ else bcoldown)
    plot(ta.sma(c_, ma1len) if showma1 and linestyle == 'Candle' else na, title='SMA 1', color=ma1col)
    plot(ta.sma(c_, ma2len) if showma2 and linestyle == 'Candle' else na, title='SMA 2', color=ma2col)
    plot(ta.ema(c_, ema1len) if showema1 and linestyle == 'Candle' else na, title='EMA 1', color=ema1col)
    plot(ta.ema(c_, ema2len) if showema2 and linestyle == 'Candle' else na, title='EMA 2', color=ema2col)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
