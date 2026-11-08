"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import bar_index, close, color, fill, hline, input, line, na, nz, plot, script, ta
from pynecore.types import Line, Persistent, Series


@script.indicator('Trend Lines for RSI, CCI, Momentum, OBV', overlay=False, max_bars_back=4000, na_bool=True)
def main(
    indi=input.string(defval='RSI', title='Indicator', options=('RSI', 'CCI', 'OBV', 'Momentum')),
    Src: Series[float] = input(defval=close, title='Source'),
    rsilen=input.int(defval=14, title='RSI Length', minval=1),
    ccilen=input.int(defval=20, title='CCI Length', minval=1),
    momlen=input.int(defval=10, title='Momentum Length', minval=1),
    prd=input.int(defval=10, title='Pivot Point Period', minval=5, maxval=50),
    PPnum=input.int(defval=3, title='Number of Pivot Point to check', minval=2, maxval=3)
):
    Rsi = ta.rsi(Src, rsilen)
    Cci = ta.cci(Src, ccilen)
    Mom = ta.cci(Src, momlen)
    src: Series = Rsi if indi == 'RSI' else Cci if indi == 'CCI' else Mom if indi == 'Momentum' else ta.obv
    hline1 = 70 if indi == 'RSI' else 100 if indi == 'CCI' else na
    hline2 = 30 if indi == 'RSI' else -100 if indi == 'CCI' else na
    h1 = hline(hline1)
    h2 = hline(hline2)
    fill(h1, h2, color=color.new(color.new('#9915FF'), 90))
    plot(src, linewidth=2)
    ph: float = na(float)
    pl: float = na(float)
    ph = ta.pivothigh(src, prd, prd)
    pl = ta.pivotlow(src, prd, prd)
    def getloc(bar_i):
        _ret = bar_index + prd - bar_i
        return _ret

    t1pos = ta.valuewhen(cast_bool(ph), bar_index, 0)
    t1val = nz(src[getloc(t1pos)])
    t2pos = ta.valuewhen(cast_bool(ph), bar_index, 1)
    t2val = nz(src[getloc(t2pos)])
    t3pos = ta.valuewhen(cast_bool(ph), bar_index, 2)
    t3val = nz(src[getloc(t3pos)])
    b1pos = ta.valuewhen(cast_bool(pl), bar_index, 0)
    b1val = nz(src[getloc(b1pos)])
    b2pos = ta.valuewhen(cast_bool(pl), bar_index, 1)
    b2val = nz(src[getloc(b2pos)])
    b3pos = ta.valuewhen(cast_bool(pl), bar_index, 2)
    b3val = nz(src[getloc(b3pos)])
    def getloval(l1, l2):
        _ret1 = b1val if l1 == 1 else b2val if l1 == 2 else b3val if l1 == 3 else 0
        _ret2 = b1val if l2 == 1 else b2val if l2 == 2 else b3val if l2 == 3 else 0
        return (_ret1, _ret2)

    def getlopos(l1, l2):
        _ret1 = b1pos if l1 == 1 else b2pos if l1 == 2 else b3pos if l1 == 3 else 0
        _ret2 = b1pos if l2 == 1 else b2pos if l2 == 2 else b3pos if l2 == 3 else 0
        return (_ret1, _ret2)

    def gethival(l1, l2):
        _ret1 = t1val if l1 == 1 else t2val if l1 == 2 else t3val if l1 == 3 else 0
        _ret2 = t1val if l2 == 1 else t2val if l2 == 2 else t3val if l2 == 3 else 0
        return (_ret1, _ret2)

    def gethipos(l1, l2):
        _ret1 = t1pos if l1 == 1 else t2pos if l1 == 2 else t3pos if l1 == 3 else 0
        _ret2 = t1pos if l2 == 1 else t2pos if l2 == 2 else t3pos if l2 == 3 else 0
        return (_ret1, _ret2)

    l1: Persistent[Line] = na(Line)
    l2: Persistent[Line] = na(Line)
    l3: Persistent[Line] = na(Line)
    t1: Persistent[Line] = na(Line)
    t2: Persistent[Line] = na(Line)
    t3: Persistent[Line] = na(Line)
    line.delete(l1)
    line.delete(l2)
    line.delete(l3)
    line.delete(t1)
    line.delete(t2)
    line.delete(t3)
    countlinelo: int = 0
    countlinehi: int = 0
    for p1 in pine_range(1, PPnum - 1, 1):
        uv1: float = 0.0
        uv2: float = 0.0
        up1: int = 0
        up2: int = 0
        for p2 in pine_range(PPnum, p1 + 1, 1):
            val1, val2 = getloval(p1, p2)
            pos1, pos2 = getlopos(p1, p2)
            if val1 > val2:
                diff = (val1 - val2) / (pos1 - pos2)
                hline__ren__ = val2 + diff
                lloc = bar_index
                lval = src
                valid: bool = True
                for x in pine_range(pos2 + 1 - prd, bar_index, 1):
                    if nz(src[getloc(x + prd)]) < hline__ren__:
                        valid = False
                    lloc = x
                    lval = hline__ren__
                    hline__ren__ = hline__ren__ + diff
                if valid:
                    uv1 = hline__ren__
                    uv2 = val2
                    up1 = lloc
                    up2 = pos2
                    break
        dv1: float = 0.0
        dv2: float = 0.0
        dp1: int = 0
        dp2: int = 0
        for p2 in pine_range(PPnum, p1 + 1, 1):
            val1, val2 = gethival(p1, p2)
            pos1, pos2 = gethipos(p1, p2)
            if val1 < val2:
                diff = (val2 - val1) / (pos1 - pos2)
                hline__ren__ = val2 - diff
                lloc = bar_index
                lval = src
                valid: bool = True
                for x in pine_range(pos2 + 1 - prd, bar_index, 1):
                    if nz(src[getloc(x + prd)]) > hline__ren__:
                        valid = False
                        break
                    lloc = x
                    lval = hline__ren__
                    hline__ren__ = hline__ren__ - diff
                if valid:
                    dv1 = hline__ren__
                    dv2 = val2
                    dp1 = lloc
                    dp2 = pos2
                    break
        if up1 != 0 and up2 != 0:
            countlinelo = countlinelo + 1
            l1 = line.new(up2 - prd, uv2, up1, uv1) if countlinelo == 1 else l1
            l2 = line.new(up2 - prd, uv2, up1, uv1) if countlinelo == 2 else l2
            l3 = line.new(up2 - prd, uv2, up1, uv1) if countlinelo == 3 else l3
        if dp1 != 0 and dp2 != 0:
            countlinehi = countlinehi + 1
            t1 = line.new(dp2 - prd, dv2, dp1, dv1) if countlinehi == 1 else t1
            t2 = line.new(dp2 - prd, dv2, dp1, dv1) if countlinehi == 2 else t2
            t3 = line.new(dp2 - prd, dv2, dp1, dv1) if countlinehi == 3 else t3


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
