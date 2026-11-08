"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    alertcondition, bar_index, close, color, fill, high, input, line, low,
    math, na, plot, script, ta
)
from pynecore.types import Line, Persistent, PersistentSeries, Series


@script.indicator('Consolidation Zones - Live', overlay=True, max_bars_back=1100, na_bool=True)
def main(
    prd=input.int(defval=10, title='Loopback Period', minval=2, maxval=50),
    conslen=input.int(defval=5, title='Min Consolidation Length', minval=2, maxval=20),
    paintcons=input(defval=True, title='Paint Consolidation Area '),
    zonecol=input(defval=color.new(color.blue, 70), title='Zone Color')
):
    hb_: float = high if ta.highestbars(prd) == 0 else na
    lb_: float = low if ta.lowestbars(prd) == 0 else na
    dir: PersistentSeries[int] = 0
    zz: Series[float] = na(float)
    pp: float = na(float)
    iff_1 = -1 if lb_ and na(hb_) else dir
    dir = 1 if hb_ and na(lb_) else iff_1
    if cast_bool(hb_) and cast_bool(lb_):
        if dir == 1:
            zz = hb_
        else:
            zz = lb_
    else:
        iff_1__0000000e__ = lb_ if lb_ else na
        zz = hb_ if hb_ else iff_1__0000000e__
    for x in pine_range(0, 1000, 1):
        if na(close) or dir != dir[x]:
            break
        if zz[x]:
            if na(pp):
                pp = zz[x]
            else:
                if dir[x] == 1 and zz[x] > pp:
                    pp = zz[x]
                if dir[x] == -1 and zz[x] < pp:
                    pp = zz[x]
    conscnt: Persistent[int] = 0
    condhigh: Persistent[float] = na(float)
    condlow: Persistent[float] = na(float)
    H_: float = ta.highest(conslen)
    L_: float = ta.lowest(conslen)
    upline: Persistent[Line] = na(Line)
    dnline: Persistent[Line] = na(Line)
    breakoutup: bool = False
    breakoutdown: bool = False
    if cast_bool(ta.change(pp)):
        if conscnt > conslen:
            if pp > condhigh:
                breakoutup = True
            if pp < condlow:
                breakoutdown = True
        if conscnt > 0 and pp <= condhigh and (pp >= condlow):
            conscnt = conscnt + 1
        else:
            conscnt = 0
    else:
        conscnt = conscnt + 1
    if conscnt >= conslen:
        if conscnt == conslen:
            condhigh = H_
            condlow = L_
        else:
            line.delete(upline)
            line.delete(dnline)
            condhigh = math.max(condhigh, high)
            condlow = math.min(condlow, low)
        upline = line.new(bar_index, condhigh, bar_index - conscnt, condhigh, color=color.red, style=line.style_dashed)
        dnline = line.new(bar_index, condlow, bar_index - conscnt, condlow, color=color.lime, style=line.style_dashed)
    fill(plot(condhigh, color=na, style=plot.style_stepline), plot(condlow, color=na, style=plot.style_stepline), color=zonecol if paintcons and conscnt > conslen else color.new(color.white, 100))
    alertcondition(breakoutup, title='Breakout Up', message='Breakout Up')
    alertcondition(breakoutdown, title='Breakout Down', message='Breakout Down')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
