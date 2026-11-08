"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    bar_index, close, color, extend, fill, high, input, line, low, math, na,
    open, plot, script, ta, time, timeframe
)
from pynecore.types import Line, Persistent, PersistentSeries, Series


@script.indicator('Support Resistance MTF', overlay=True, max_bars_back=4900, na_bool=True)
def main(
    src=input.string(defval='High/Low', title='Source', options=('High/Low', 'Close/Open')),
    TimeframeU=input.string(defval='Auto', title='Higher Time Frame', options=('Auto', '15', '30', '60', '120', '180', '240', '720', 'D', 'W', '2W', 'M', '3M', '6M', '12M')),
    prd=input.int(defval=10, title='Period for Highest/Lowest Bars', minval=1),
    resistancecol=input(defval=color.red, title='Resistance Color'),
    supportcol=input(defval=color.lime, title='Support Color'),
    Transp=input.int(defval=80, title='Transparency for Zones', minval=0, maxval=100),
    extendlines=input(defval=False, title='Extend Lines')
):
    Timeframe = timeframe.period
    if TimeframeU == 'Auto':
        Timeframe = '15' if timeframe.period == '1' else '15' if timeframe.period == '3' else '60' if timeframe.period == '5' else '60' if timeframe.period == '15' else '120' if timeframe.period == '30' else '120' if timeframe.period == '45' else '240' if timeframe.period == '60' else 'D' if timeframe.period == '120' else 'D' if timeframe.period == '180' else 'D' if timeframe.period == '240' else 'W' if timeframe.period == 'D' else 'M' if timeframe.period == 'W' else '12M'
    else:
        Timeframe = TimeframeU
    hc: PersistentSeries[float] = na(float)
    lc: PersistentSeries[float] = na(float)
    srch = high if src == 'High/Low' else math.max(close, open)
    srcl = low if src == 'High/Low' else math.min(close, open)
    hc = srch if ta.highestbars(srch, prd) == 0 else hc
    lc = srcl if ta.lowestbars(srcl, prd) == 0 else lc
    hcp = plot(hc, color=resistancecol if hc == hc[1] else na)
    lcp = plot(lc, color=supportcol if lc == lc[1] else na)
    newbar: Series[bool] = ta.change(time(Timeframe)) != 0
    htfh: Persistent[float] = na(float)
    htfl: Persistent[float] = na(float)
    if newbar:
        htfh = srch
        htfl = srcl
    else:
        htfh = math.max(htfh, srch)
        htfl = math.min(htfl, srcl)
    def highestbar(src: Series, len):
        __hist_newbar__: Series[bool] = newbar[0]
        ll: int = 1
        if len > 1:
            for x in pine_range(0, 4000, 1):
                if na(__hist_newbar__[x]) or na(close[x + 1]):
                    break
                if __hist_newbar__[x]:
                    if src <= src[x + 1]:
                        break
                    ll = ll + 1
                    if ll >= len:
                        break
        ret = ll >= len
        return ret

    def lowestbar(src: Series, len):
        __hist_newbar__: Series[bool] = newbar[0]
        ll: int = 1
        if len > 1:
            for x in pine_range(0, 4000, 1):
                if na(__hist_newbar__[x]) or na(close[x + 1]):
                    break
                if __hist_newbar__[x]:
                    if src >= src[x + 1]:
                        break
                    ll = ll + 1
                    if ll >= len:
                        break
        ret = ll >= len
        return ret

    hh: PersistentSeries[float] = 0
    ll: PersistentSeries[float] = 0
    hbar: bool = highestbar(htfh, prd)
    lbar: bool = lowestbar(htfl, prd)
    hh = htfh if hbar else hh
    ll = htfl if lbar else ll
    hhp = plot(hh, color=resistancecol if hh == hh[1] else na)
    llp = plot(ll, color=supportcol if ll == ll[1] else na)
    fill(hhp, hcp, color=color.new(resistancecol, Transp) if hc == hc[1] and hh == hh[1] else na)
    fill(llp, lcp, color=color.new(supportcol, Transp) if lc == lc[1] and ll == ll[1] else na)
    if extendlines:
        s1: Persistent[Line] = na(Line)
        s2: Persistent[Line] = na(Line)
        r1: Persistent[Line] = na(Line)
        r2: Persistent[Line] = na(Line)
        line.delete(s1)
        line.delete(s2)
        line.delete(r1)
        line.delete(r2)
        s1 = line.new(bar_index, lc, bar_index - 1, lc, color=supportcol, extend=extend.left)
        s2 = line.new(bar_index, ll, bar_index - 1, ll, color=supportcol, extend=extend.left)
        r1 = line.new(bar_index, hc, bar_index - 1, hc, color=resistancecol, extend=extend.left)
        r2 = line.new(bar_index, hh, bar_index - 1, hh, color=resistancecol, extend=extend.left)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)