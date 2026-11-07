"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bar_index, close, color, input, line, location, math, na, nz, plotshape,
    script, shape, strategy, ta
)
from pynecore.types import Line, Persistent, PersistentSeries


@script.strategy('ABCD Strategy', shorttitle='ABCDS', overlay=True, commission_value=0.04, margin_long=0, margin_short=0, initial_capital=1000000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    len=input(5)
):
    def calcdev(fprice, lprice, fbars, lbars):
        rise = lprice - fprice
        run = lbars - fbars
        avg = rise / run
        return (bar_index - lbars) * avg + lprice

    ph = ta.pivothigh(len, len)
    pl = ta.pivotlow(len, len)
    ishigh: PersistentSeries[bool] = False
    ishigh = ishigh[1]
    currph: Persistent[float] = 0.0
    currphb: Persistent[int] = 0
    currph = nz(currph)
    currphb = nz(currphb)
    oldph: Persistent[float] = 0.0
    oldphb: Persistent[int] = 0
    oldph = nz(oldph)
    oldphb = nz(oldphb)
    currpl: Persistent[float] = 0.0
    currplb: Persistent[int] = 0
    currpl = nz(currpl)
    currplb = nz(currplb)
    oldpl: Persistent[float] = 0.0
    oldplb: Persistent[int] = 0
    oldpl = nz(oldpl)
    oldplb = nz(oldplb)
    if not na(ph):
        ishigh = True
        oldph = currph
        oldphb = currphb
        currph = ph
        currphb = bar_index[len]
    else:
        if not na(pl):
            ishigh = False
            oldpl = currpl
            oldplb = currplb
            currpl = pl
            currplb = bar_index[len]
    endHighPoint = calcdev(oldph, currph, oldphb, currphb)
    endLowPoint = calcdev(oldpl, currpl, oldplb, currplb)
    plotshape(ph, style=shape.triangledown, color=color.red, location=location.abovebar, offset=-len)
    plotshape(pl, style=shape.triangleup, color=color.green, location=location.belowbar, offset=-len)
    lnhigher: PersistentSeries[Line] = na(Line)
    lnlower: PersistentSeries[Line] = na(Line)
    lnhigher = line.new(oldphb, oldph, bar_index, endHighPoint)
    lnlower = line.new(oldplb, oldpl, bar_index, endLowPoint)
    line.delete(lnhigher[1])
    line.delete(lnlower[1])
    formlong = oldphb < oldplb and oldplb < currphb and (currphb < currplb)
    longratio1 = (currph - oldpl) / (oldph - oldpl)
    longratio2 = (currph - currpl) / (currph - oldpl)
    formshort = oldplb < oldphb and oldphb < currplb and (currplb < currphb)
    shortratio1 = (oldph - currpl) / (oldph - oldpl)
    shortratio2 = (currph - currpl) / (oldph - currpl)
    signalid: PersistentSeries[int] = 0
    signalid = nz(signalid[1])
    longCond = formlong and longratio1 < 0.786 and (longratio1 > 0.5) and (longratio2 > 1) and (longratio2 < 1.414) and (close < oldph) and (close > currpl) and (signalid != oldplb)
    if longCond:
        signalid = oldplb
        longsl = currpl - ta.tr
        longtp = (close - longsl) * 1.5 + close
        strategy.entry('Long', strategy.long)
        strategy.exit('Exit Long', 'Long', limit=math.min(longtp, oldph), stop=longsl)
    shortCond = formshort and shortratio1 < 0.786 and (shortratio1 > 0.5) and (shortratio2 > 1.1) and (shortratio2 < 1.414) and (close > oldpl) and (close < currph) and (signalid != oldphb)
    if shortCond:
        signalid = oldphb
        shortsl = currph + ta.tr
        shorttp = close - (shortsl - close) * 1.5
        strategy.entry('Short', strategy.short)
        strategy.exit('Exit Short', 'Short', limit=math.max(shorttp, oldpl), stop=shortsl)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
