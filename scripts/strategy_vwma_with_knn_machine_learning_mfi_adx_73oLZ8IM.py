"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    array, bgcolor, color, fixnan, high, input, low, math, na, nz, ohlc4,
    open, plot, script, strategy, ta, volume
)
from pynecore.types import Persistent, Series


@script.strategy(title='VWMA with kNN Machine Learning: MFI/ADX by lastguru', shorttitle='VWMA + kNN: MFI/ADX', overlay=True, default_qty_type=strategy.percent_of_equity, default_qty_value=100, margin_long=0, margin_short=0, initial_capital=100000, close_by_id=True, na_bool=True)
def main(
    SRC: Series[float] = input(title='Source', defval=open),
    FAST=input(title='Fast Length', defval=13),
    SLOW=input(title='Slow Length', defval=19),
    APPLY=input(title='Apply kNN filter', defval=True),
    FILTER=input(title='Filter Length', defval=13),
    SMOOTH=input(title='Filter Smoothing', defval=6),
    KNN=input(title='kNN nearest neighbors (k)', defval=45),
    DIST=input(title='kNN minimum difference', defval=2),
    BACKGROUND=input(title='Draw background', defval=False)
):
    knn1: Persistent[list[float]] = array.new_float(1, 0)
    knn2: Persistent[list[float]] = array.new_float(1, 0)
    knnp: Persistent[list[float]] = array.new_float(1, 0)
    knnr: Persistent[list[float]] = array.new_float(1, 0)
    def _knnStore(p1, p2, src):
        prevp1: Persistent[float] = 0.0
        prevp2: Persistent[float] = 0.0
        prevsrc: Persistent[float] = 0.0
        array.push(knn1, prevp1)
        array.push(knn2, prevp2)
        array.push(knnp, prevsrc)
        array.push(knnr, 1 if src >= prevsrc else -1)
        prevp1 = p1
        prevp2 = p2
        prevsrc = src
        return prevsrc

    def _knnGet(arr1, arr2, k):
        sarr = array.copy(arr1)
        array.sort(sarr)
        ss = array.slice(sarr, 0, math.min(k, array.size(sarr)))
        m = array.max(ss)
        out: list[float] = array.new_float(0)
        for i in pine_range(0, array.size(arr1) - 1, 1):
            if array.get(arr1, i) <= m:
                array.push(out, array.get(arr2, i))
        return out

    def _knnDistance(p1, p2):
        dist: list[float] = array.new_float(0)
        n = array.size(knn1) - 1
        for i in pine_range(0, n, 1):
            d = math.sqrt(math.pow(p1 - array.get(knn1, i), 2) + math.pow(p2 - array.get(knn2, i), 2))
            array.push(dist, d)
        return dist

    def _knn(p1, p2, k):
        slice = _knnGet(_knnDistance(p1, p2), array.copy(knnr), k)
        knn = array.sum(slice)
        return knn

    fastMA = ta.vwma(SRC, FAST)
    slowMA = ta.vwma(SRC, SLOW)
    def _rma(src, length):
        out: Series[float] = 0.0
        out = ((length - 1) * nz(out[1]) + src) / length
        return out

    def _dmi(len, smooth):
        up = ta.change(high)
        down = -ta.change(low)
        plusDM = na if na(up) else up if up > down and up > 0 else 0
        minusDM = na if na(down) else down if down > up and down > 0 else 0
        trur = _rma(ta.tr, len)
        plus = fixnan(100 * _rma(plusDM, len) / trur)
        minus = fixnan(100 * _rma(minusDM, len) / trur)
        sum = plus + minus
        adx = 100 * _rma(math.abs(plus - minus) / (1 if sum == 0 else sum), smooth)
        return (plus, minus, adx)

    diplus, diminus, adx = _dmi(FILTER, SMOOTH)
    def _rsi(upper, lower):
        if lower == 0:
            pass
        if upper == 0:
            pass
        return 100.0 - 100.0 / (1.0 + upper / lower)

    mfiUp = math.sum(volume * (0 if ta.change(ohlc4) <= 0 else ohlc4), FILTER)
    mfiDown = math.sum(volume * (0 if ta.change(ohlc4) >= 0 else ohlc4), FILTER)
    mfi = _rsi(mfiUp, mfiDown)
    longCondition = ta.crossover(fastMA, slowMA)
    shortCondition = ta.crossunder(fastMA, slowMA)
    if longCondition or shortCondition:
        _knnStore(adx, mfi, SRC)
    filter = _knn(adx, mfi, KNN)
    bgcolor((color.green if filter >= 0 else color.red) if BACKGROUND else na)
    plot(fastMA, color=color.new(color.red, 0))
    plot(slowMA, color=color.new(color.green, 0))
    if longCondition and (not APPLY or filter >= DIST):
        strategy.entry('Long', strategy.long)
    if shortCondition and (not APPLY or filter <= -DIST):
        strategy.entry('Short', strategy.short)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
