"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import alert, close, color, fill, input, na, nz, plot, script, ta
from pynecore.types import PersistentSeries, Series


@script.indicator(title='[SHK] Schaff Trend Cycle (STC)', shorttitle='STC', overlay=False)
def main(
    EEEEEE=input(12, 'Length'),
    BBBB=input(26, 'FastLength'),
    BBBBB=input(50, 'SlowLength'),
    __input_3__=input(0.5)
):
    def AAAA(BBB, BBBB, BBBBB):
        fastMA = ta.ema(BBB, BBBB)
        slowMA = ta.ema(BBB, BBBBB)
        AAAA__00000007__ = fastMA - slowMA
        return AAAA__00000007__

    def AAAAA(EEEEEE, BBBB, BBBBB):
        AAA = __input_3__
        CCCCC: PersistentSeries[float] = 0.0
        DDD: PersistentSeries[float] = 0.0
        DDDDDD: PersistentSeries[float] = 0.0
        EEEEE: PersistentSeries[float] = 0.0
        BBBBBB = AAAA(close, BBBB, BBBBB)
        CCC = ta.lowest(BBBBBB, EEEEEE)
        CCCC = ta.highest(BBBBBB, EEEEEE) - CCC
        CCCCC = (BBBBBB - CCC) / CCCC * 100 if CCCC > 0 else nz(CCCCC[1])
        DDD = CCCCC if na(DDD[1]) else DDD[1] + AAA * (CCCCC - DDD[1])
        DDDD = ta.lowest(DDD, EEEEEE)
        DDDDD = ta.highest(DDD, EEEEEE) - DDDD
        DDDDDD = (DDD - DDDD) / DDDDD * 100 if DDDDD > 0 else nz(DDDDDD[1])
        EEEEE = DDDDDD if na(EEEEE[1]) else EEEEE[1] + AAA * (DDDDDD - EEEEE[1])
        return EEEEE

    mAAAAA: Series = AAAAA(EEEEEE, BBBB, BBBBB)
    mColor = color.new(color.green, 20) if mAAAAA > mAAAAA[1] else color.new(color.red, 20)
    if mAAAAA[3] <= mAAAAA[2] and mAAAAA[2] > mAAAAA[1] and (mAAAAA > 75):
        alert('Red', alert.freq_once_per_bar)
    if mAAAAA[3] >= mAAAAA[2] and mAAAAA[2] < mAAAAA[1] and (mAAAAA < 25):
        alert('Green', alert.freq_once_per_bar)
    plot(mAAAAA, color=mColor, title='STC', linewidth=2)
    ul = plot(25, color=color.new(color.gray, 70))
    ll = plot(75, color=color.new(color.gray, 70))
    fill(ul, ll, color=color.new(color.gray, 96))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
