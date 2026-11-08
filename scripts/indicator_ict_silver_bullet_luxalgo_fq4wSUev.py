"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_bool
from pynecore.core.pine_method import method, method_call
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    array, bar_index, barstate, box, close, color, extend, high, input, line,
    location, low, math, max_bars_back, na, nz, plotchar, position, script, size, syminfo, ta,
    table, time, timeframe
)
from pynecore.types import Box, Color, Line, NA, Persistent, Series


@udt
class piv:
    b: int = na(int)
    p: float = na(float)
    br: bool = na(bool)


@udt
class ZZ:
    d: list[int] = na(list)
    x: list[int] = na(list)
    y: list[float] = na(list)
    l: list[Line] = na(list)


@udt
class FVG:
    box__ren__: Box = na(Box)
    active: bool = na(bool)
    current: bool = na(bool)


@udt
class actLine:
    ln: Line = na(Line)
    active: bool = na(bool)


@udt
class aPiv:
    GN_swingH: 'list[piv]' = na(list)
    GN_swingL: 'list[piv]' = na(list)
    GN_mnPiv: float = na(float)
    GN_mxPiv: float = na(float)
    GN_targHi: list[Line] = na(list)
    GN_targLo: list[Line] = na(list)
    LN_swingH: 'list[piv]' = na(list)
    LN_swingL: 'list[piv]' = na(list)
    LN_mnPiv: float = na(float)
    LN_mxPiv: float = na(float)
    LN_targHi: list[Line] = na(list)
    LN_targLo: list[Line] = na(list)
    AM_swingH: 'list[piv]' = na(list)
    AM_swingL: 'list[piv]' = na(list)
    AM_mnPiv: float = na(float)
    AM_mxPiv: float = na(float)
    AM_targHi: list[Line] = na(list)
    AM_targLo: list[Line] = na(list)
    PM_swingH: 'list[piv]' = na(list)
    PM_swingL: 'list[piv]' = na(list)
    PM_mnPiv: float = na(float)
    PM_mxPiv: float = na(float)
    PM_targHi: list[Line] = na(list)
    PM_targLo: list[Line] = na(list)


@script.indicator('ICT Silver Bullet [LuxAlgo]', shorttitle='LuxAlgo - ICT Silver Bullet', max_lines_count=500, max_boxes_count=500, max_labels_count=500, overlay=True, na_bool=True)
def main(
    left=input.int(5, '', minval=1, maxval=20, group='Swings settings (left)'),
    showSB=input.bool(True, 'Show SB session', inline='SB', group='Silver Bullet session'),
    col_SB=input.color(color.new('#B2B5BE50'), '     ', inline='SB', group='Silver Bullet session'),
    choice=input.string('Super-Strict', '', inline='fvg', group='FVG', options=('All FVG', 'Only FVG in the same direction of trend', 'Strict', 'Super-Strict')),
    cBullFVG=input.color(color.new('#4DD0E160'), '', inline='fvg', group='FVG'),
    cBearFVG=input.color(color.new('#FFC1B160'), '', inline='fvg', group='FVG'),
    extend__ren__=input.bool(True, 'extend', inline='fvg', group='FVG'),
    opt=input.string('previous session (similar)', '', inline='TG', group='Targets          -         Support/Resistance', options=('previous session (any)', 'previous session (similar)')),
    cSupLine=input.color(color.new('#B22833'), '', inline='TG', group='Targets          -         Support/Resistance'),
    cResLine=input.color(color.new('#3E89FA'), '', inline='TG', group='Targets          -         Support/Resistance'),
    keep=input.bool(True, 'Keep lines (only in [super-]strict mode)', group='Targets          -         Support/Resistance'),
    showT=input.bool(False, title='MSS ~ session', group='Show'),
    showZZ=input.bool(False, title='Trend', group='Show')
):
    superstrict = choice == 'Super-Strict'
    iTrend = choice != 'All FVG'
    strict = choice == 'Strict'
    stricty = superstrict or strict
    prev = opt == 'previous session (any)'
    n = bar_index
    maxSize: int = 250
    minT = syminfo.mintick
    a: Persistent[aPiv] = aPiv(GN_swingH=array.new(1, piv(na, na)), GN_swingL=array.new(1, piv(na, na)), GN_mnPiv=10000000.0, GN_mxPiv=0, GN_targHi=array.new_line(), GN_targLo=array.new_line(), LN_swingH=array.new(1, piv(na, na)), LN_swingL=array.new(1, piv(na, na)), LN_mnPiv=10000000.0, LN_mxPiv=0, LN_targHi=array.new_line(), LN_targLo=array.new_line(), AM_swingH=array.new(1, piv(na, na)), AM_swingL=array.new(1, piv(na, na)), AM_mnPiv=10000000.0, AM_mxPiv=0, AM_targHi=array.new_line(), AM_targLo=array.new_line(), PM_swingH=array.new(1, piv(na, na)), PM_swingL=array.new(1, piv(na, na)), PM_mnPiv=10000000.0, PM_mxPiv=0, PM_targHi=array.new_line(), PM_targLo=array.new_line())
    aZZ: Persistent[ZZ] = ZZ(array.new_int(maxSize, 0), array.new_int(maxSize, 0), array.new_float(maxSize, na), array.new_line(maxSize, na))
    bFVG_bull: Persistent[list[FVG]] = array.new(1, FVG(box__ren__=box.new(na, na, na, na), active=NA(bool)))
    bFVG_bear: Persistent[list[FVG]] = array.new(1, FVG(box__ren__=box.new(na, na, na, na), active=NA(bool)))
    min: Persistent[float] = 10000000.0
    max: Persistent[float] = 0.0
    hilo: Persistent[list[float]] = array.from_items(0, 10000000.0)
    aTrend: Persistent[list[int]] = array.from_items(0)
    l_SB: Persistent[list[Line]] = array.new_line()
    highs: Persistent[list[actLine]] = array.new(0, NA(actLine))
    lows: Persistent[list[actLine]] = array.new(0, NA(actLine))
    tab: Persistent = table.new(position=position.top_right, columns=1, rows=1, bgcolor=NA(Color), border_width=1)
    ph = ta.pivothigh(left, 1)
    pl = ta.pivotlow(left, 1)
    @method
    def type(str__ren__: str):
        return syminfo.type == 'stock' and str__ren__ == 'stock' or (syminfo.type == 'futures' and str__ren__ == 'futures') or (syminfo.type == 'index' and str__ren__ == 'index') or (syminfo.type == 'forex' and str__ren__ == 'forex') or (syminfo.type == 'crypto' and str__ren__ == 'crypto') or (syminfo.type == 'fund' and str__ren__ == 'fund')

    @method
    def timeSess(timezone: str, session__ren__: str):
        return time(timeframe.period, session__ren__, timezone)

    SB_LN_per: Series = method_call(timeSess, 'America/New_York', '0300-0400')
    SB_AM_per: Series = method_call(timeSess, 'America/New_York', '1000-1100')
    SB_PM_per: Series = method_call(timeSess, 'America/New_York', '1400-1500')
    is_in_SB: Series = cast_bool(SB_LN_per) or cast_bool(SB_AM_per) or cast_bool(SB_PM_per)
    strSB = is_in_SB and (not is_in_SB[1])
    strLN = cast_bool(SB_LN_per) and (not SB_LN_per[1])
    strAM = cast_bool(SB_AM_per) and (not SB_AM_per[1])
    strPM = cast_bool(SB_PM_per) and (not SB_PM_per[1])
    endSB: Series = not is_in_SB and is_in_SB[1]
    endLN = not SB_LN_per and cast_bool(SB_LN_per[1])
    endAM = not SB_AM_per and cast_bool(SB_AM_per[1])
    endPM = not SB_PM_per and cast_bool(SB_PM_per[1])
    minimum_trade_framework = syminfo.mintick * 15 * 10 if method_call(type, 'forex') else syminfo.mintick * 40 if method_call(type, 'index') or method_call(type, 'futures') else 0
    @method
    def in_out(aZZ: ZZ, d__0000005d__: int, x1: int, y1: float, x2: int, y2: float):
        array.unshift(aZZ.d, d__0000005d__)
        array.unshift(aZZ.x, x2)
        array.unshift(aZZ.y, y2)
        array.pop(aZZ.d)
        array.pop(aZZ.x)
        array.pop(aZZ.y)
        __block_result__ = na
        if showZZ:
            array.unshift(aZZ.l, line.new(x1, y1, x2, y2, color=color.new(color.blue, 50)))
            __block_result__ = method_call('delete', array.pop(aZZ.l))
        return __block_result__

    def f_setTrend():
        MSS_dir = array.get(aTrend, 0)
        iH = 2 if array.get(aZZ.d, 2) == 1 else 1
        iL = 2 if array.get(aZZ.d, 2) == -1 else 1
        __block_result_1__ = na
        if close > array.get(aZZ.y, iH) and array.get(aZZ.d, iH) == 1 and (MSS_dir < 1):
            __block_result_1__ = array.set(aTrend, 0, 1)
        elif close < array.get(aZZ.y, iL) and array.get(aZZ.d, iL) == -1 and (MSS_dir > -1):
            __block_result_1__ = array.set(aTrend, 0, -1)
        return __block_result_1__

    def f_swings(start, end, str__ren__, col, min, max):
        max_bars_back(time, 1000)
        MSS_dir: Persistent[int] = array.get(aTrend, 0)
        x2 = n - 1
        swingH: list[piv] = na(list[piv])
        swingL: list[piv] = na(list[piv])
        mnPiv: float = na(float)
        mxPiv: float = na(float)
        targHi: list[Line] = na(list[Line])
        targLo: list[Line] = na(list[Line])
        active: bool = na(bool)
        __switch__ = str__ren__
        if __switch__ == 'GN':
            swingH = a.GN_swingH
            swingL = a.GN_swingL
            mnPiv = a.GN_mnPiv
            mxPiv = a.GN_mxPiv
            targHi = a.GN_targHi
            targLo = a.GN_targLo
            active = is_in_SB
        elif __switch__ == 'LN':
            swingH = a.LN_swingH
            swingL = a.LN_swingL
            mnPiv = a.LN_mnPiv
            mxPiv = a.LN_mxPiv
            targHi = a.LN_targHi
            targLo = a.LN_targLo
            active = SB_LN_per
        elif __switch__ == 'AM':
            swingH = a.AM_swingH
            swingL = a.AM_swingL
            mnPiv = a.AM_mnPiv
            mxPiv = a.AM_mxPiv
            targHi = a.AM_targHi
            targLo = a.AM_targLo
            active = SB_AM_per
        elif __switch__ == 'PM':
            swingH = a.PM_swingH
            swingL = a.PM_swingL
            mnPiv = a.PM_mnPiv
            mxPiv = a.PM_mxPiv
            targHi = a.PM_targHi
            targLo = a.PM_targLo
            active = SB_PM_per
        if start:
            array.set(hilo, 0, 0)
            array.set(hilo, 1, 10000000.0)
            if not keep if stricty else True:
                while array.size(highs) > 0:
                    get = array.pop(highs)
                    method_call('delete', get.ln)
                while array.size(lows) > 0:
                    get = array.pop(lows)
                    method_call('delete', get.ln)
                while array.size(targHi) > 0:
                    method_call('delete', array.pop(targHi))
                while array.size(targLo) > 0:
                    method_call('delete', array.pop(targLo))
                while array.size(a.GN_targHi) > 0:
                    method_call('delete', array.pop(a.GN_targHi))
                while array.size(a.LN_targHi) > 0:
                    method_call('delete', array.pop(a.LN_targHi))
                while array.size(a.AM_targHi) > 0:
                    method_call('delete', array.pop(a.AM_targHi))
                while array.size(a.PM_targHi) > 0:
                    method_call('delete', array.pop(a.PM_targHi))
                while array.size(a.GN_targLo) > 0:
                    method_call('delete', array.pop(a.GN_targLo))
                while array.size(a.LN_targLo) > 0:
                    method_call('delete', array.pop(a.LN_targLo))
                while array.size(a.AM_targLo) > 0:
                    method_call('delete', array.pop(a.AM_targLo))
                while array.size(a.PM_targLo) > 0:
                    method_call('delete', array.pop(a.PM_targLo))
        if active:
            array.set(hilo, 0, math.max(array.get(hilo, 0), high))
            array.set(hilo, 1, math.min(array.get(hilo, 1), low))
        if cast_bool(ph):
            if ph > mxPiv:
                mxPiv = ph
            if array.size(swingH) > 0:
                for i in pine_range(array.size(swingH) - 1, 0, 1):
                    get = array.get(swingH, i)
                    if ph >= get.p:
                        array.remove(swingH, i)
            array.unshift(swingH, piv(n - 1, ph))
            if str__ren__ == 'GN' or str__ren__ == 'LN':
                dir = array.get(aZZ.d, 0)
                x1 = array.get(aZZ.x, 0)
                y1 = array.get(aZZ.y, 0)
                y2 = nz(high[1])
                if dir < 1:
                    in_out(aZZ, 1, x1, y1, x2, y2)
                else:
                    if dir == 1 and ph > y1:
                        array.set(aZZ.x, 0, x2)
                        array.set(aZZ.y, 0, y2)
                        if showZZ:
                            method_call('set_xy2', array.get(aZZ.l, 0), x2, y2)
        if cast_bool(pl):
            if pl < mnPiv:
                mnPiv = pl
            if array.size(swingL) > 0:
                for i in pine_range(array.size(swingL) - 1, 0, 1):
                    get = array.get(swingL, i)
                    if pl <= get.p:
                        array.remove(swingL, i)
            array.unshift(swingL, piv(n - 1, pl))
            if str__ren__ == 'GN' or str__ren__ == 'LN':
                dir = array.get(aZZ.d, 0)
                x1 = array.get(aZZ.x, 0)
                y1 = array.get(aZZ.y, 0)
                y2 = nz(low[1])
                if dir > -1:
                    in_out(aZZ, -1, x1, y1, x2, y2)
                else:
                    if dir == -1 and pl < y1:
                        array.set(aZZ.x, 0, x2)
                        array.set(aZZ.y, 0, y2)
                        if showZZ:
                            method_call('set_xy2', array.get(aZZ.l, 0), x2, y2)
        iH = 2 if array.get(aZZ.d, 2) == 1 else 1
        iL = 2 if array.get(aZZ.d, 2) == -1 else 1
        if close > array.get(aZZ.y, iH) and array.get(aZZ.d, iH) == 1 and (MSS_dir < 1):
            MSS_dir = 1
            if active and showT:
                line.new(array.get(aZZ.x, iH), array.get(aZZ.y, iH), n, array.get(aZZ.y, iH), color=cResLine, width=2)
        elif close < array.get(aZZ.y, iL) and array.get(aZZ.d, iL) == -1 and (MSS_dir > -1):
            MSS_dir = -1
            if active and showT:
                line.new(array.get(aZZ.x, iL), array.get(aZZ.y, iL), n, array.get(aZZ.y, iL), color=cSupLine, width=2)
        if end:
            sz = array.size(swingH)
            if sz > 0:
                for i in pine_range(0, sz - 1, 1):
                    y__000000fb__ = array.get(swingH, i).p
                    if y__000000fb__ > (min if stricty else array.get(hilo, 0)):
                        array.unshift(targHi, line.new(array.get(swingH, i).b, y__000000fb__, n, y__000000fb__, color=cResLine))
                        array.unshift(highs, actLine(line.new(n, y__000000fb__, n, y__000000fb__, color=cResLine), True))
            sz = array.size(swingL)
            if sz > 0:
                for i in pine_range(0, sz - 1, 1):
                    y__00000107__ = array.get(swingL, i).p
                    if y__00000107__ < (max if stricty else array.get(hilo, 1)):
                        array.unshift(targLo, line.new(array.get(swingL, i).b, y__00000107__, n, y__00000107__, color=cSupLine))
                        array.unshift(lows, actLine(line.new(n, y__00000107__, n, y__00000107__, color=cSupLine), True))
            array.clear(swingH)
            array.clear(swingL)
            mnPiv = 10000000.0
            mxPiv = 0
        if showZZ:
            if cast_bool(ph) or cast_bool(pl):
                method_call('set_color', array.get(aZZ.l, 0), cResLine if MSS_dir == 1 else cSupLine)
        return array.set(aTrend, 0, MSS_dir)

    f_setTrend()
    trend = array.get(aTrend, 0)
    targetHi: bool = False
    targetLo: bool = False
    hSz = array.size(highs)
    if hSz > 200:
        method_call('delete', array.pop(highs).ln)
    hSz = array.size(highs)
    if hSz > 0:
        for i in pine_range(0, hSz - 1, 1):
            get = array.get(highs, i)
            if get.active:
                method_call('set_x2', get.ln, n)
                if high > method_call('get_y2', get.ln):
                    get.active = False
                    targetHi = True
    lSz = array.size(lows)
    if lSz > 200:
        method_call('delete', array.pop(lows).ln)
    lSz = array.size(lows)
    if lSz > 0:
        for i in pine_range(0, lSz - 1, 1):
            get = array.get(lows, i)
            if get.active:
                method_call('set_x2', get.ln, n)
                if low < method_call('get_y2', get.ln):
                    get.active = False
                    targetLo = True
    if array.size(l_SB) > 100:
        method_call('delete', array.pop(l_SB))
    if strSB:
        min = 10000000.0
        max = 0.0
        if showSB:
            array.unshift(l_SB, line.new(n, close, n, close + minT, color=col_SB, extend=extend.both))
        for i in pine_range(0, array.size(bFVG_bull) - 1, 1):
            get = array.get(bFVG_bull, i)
            if n > method_call('get_right', get.box__ren__) - 1:
                if get.current == True:
                    get.current = False
        for i in pine_range(0, array.size(bFVG_bear) - 1, 1):
            get = array.get(bFVG_bear, i)
            if n > method_call('get_right', get.box__ren__) - 1:
                if get.current == True:
                    get.current = False
    if is_in_SB:
        trend = array.get(aTrend, 0)
        if iTrend:
            __switch_2__ = trend
            if __switch_2__ == 1:
                if low > high[2]:
                    array.unshift(bFVG_bull, FVG(box__ren__=box.new(n - 2, low, n, high[2], border_color=NA(Color), bgcolor=cBullFVG), active=False, current=True))
            else:
                if high < low[2]:
                    array.unshift(bFVG_bear, FVG(box__ren__=box.new(n - 2, low[2], n, high, border_color=NA(Color), bgcolor=cBearFVG), active=False, current=True))
        else:
            if low > high[2]:
                array.unshift(bFVG_bull, FVG(box__ren__=box.new(n, low, n, high[2], border_color=NA(Color), bgcolor=cBullFVG), active=False, current=True))
            if high < low[2]:
                array.unshift(bFVG_bear, FVG(box__ren__=box.new(n, low[2], n, high, border_color=NA(Color), bgcolor=cBearFVG), active=False, current=True))
    if endSB:
        if showSB:
            array.unshift(l_SB, line.new(n, close, n, close + minT, color=col_SB, extend=extend.both))
    if array.size(bFVG_bull) > 0:
        for i in pine_range(0, array.size(bFVG_bull) - 1, 1):
            get = array.get(bFVG_bull, i)
            bLeft = method_call('get_left', get.box__ren__)
            bTop = method_call('get_top', get.box__ren__)
            bBot = method_call('get_bottom', get.box__ren__)
            if n - bLeft < 1000:
                if get.current:
                    if is_in_SB:
                        if close < bBot:
                            if superstrict:
                                get.current = False
                                method_call('set_bgcolor', get.box__ren__, color.new(color.blue, 100))
                                method_call('set_right', get.box__ren__, bLeft)
                            if superstrict or strict:
                                get.active = False
                        else:
                            if extend__ren__:
                                if get.active:
                                    method_call('set_right', get.box__ren__, n)
                        if not get.active:
                            if low < bTop and close > bBot:
                                get.active = True
                                if extend__ren__:
                                    method_call('set_right', get.box__ren__, n)
                    if endSB:
                        if get.active:
                            if strict:
                                if close < bBot:
                                    get.active = False
                            if superstrict:
                                if close < bTop:
                                    get.active = False
                        if not get.active:
                            method_call('set_bgcolor', get.box__ren__, color.new(color.blue, 100))
                            method_call('set_right', get.box__ren__, bLeft)
                        if get.active:
                            min = math.min(min, bBot + minimum_trade_framework)
                            if extend__ren__:
                                method_call('set_right', get.box__ren__, n)
                    if endSB[1]:
                        get.active = False
    if array.size(bFVG_bear) > 0:
        for i in pine_range(0, array.size(bFVG_bear) - 1, 1):
            get = array.get(bFVG_bear, i)
            bLeft = method_call('get_left', get.box__ren__)
            bTop = method_call('get_top', get.box__ren__)
            bBot = method_call('get_bottom', get.box__ren__)
            if n - bLeft < 1000:
                if get.current:
                    if is_in_SB:
                        if close > bTop:
                            if superstrict:
                                get.current = False
                                method_call('set_bgcolor', get.box__ren__, color.new(color.blue, 100))
                                method_call('set_right', get.box__ren__, bLeft)
                            if superstrict or strict:
                                get.active = False
                        else:
                            if extend__ren__:
                                if get.active:
                                    method_call('set_right', get.box__ren__, n)
                        if not get.active:
                            if high > bBot and close < bTop:
                                get.active = True
                                if extend__ren__:
                                    method_call('set_right', get.box__ren__, n)
                    if endSB:
                        if get.active:
                            if strict:
                                if close > bTop:
                                    get.active = False
                            if superstrict:
                                if close > bBot:
                                    get.active = False
                        if not get.active:
                            method_call('set_bgcolor', get.box__ren__, color.new(color.blue, 100))
                            method_call('set_right', get.box__ren__, bLeft)
                        if get.active:
                            max = math.max(max, bTop - minimum_trade_framework)
                            if extend__ren__:
                                method_call('set_right', get.box__ren__, n)
                    if endSB[1]:
                        get.active = False
    if prev:
        f_swings(strSB, endSB, 'GN', col_SB, min, max)
    else:
        f_swings(strLN, endLN, 'LN', col_SB, min, max)
        f_swings(strAM, endAM, 'AM', col_SB, min, max)
        f_swings(strPM, endPM, 'PM', col_SB, min, max)
    tfs = 60 / (timeframe.in_seconds(timeframe.period) / 60) / 2
    plotchar(not na(SB_LN_per) and na(SB_LN_per[1]) and showSB, title='3-4 AM', location=location.top, text='3-4 AM\nNY', color=NA(Color), textcolor=col_SB, offset=tfs)
    plotchar(not na(SB_AM_per) and na(SB_AM_per[1]) and showSB, title='10-11 AM', location=location.top, text='10-11 AM\nNY', color=NA(Color), textcolor=col_SB, offset=tfs)
    plotchar(not na(SB_PM_per) and na(SB_PM_per[1]) and showSB, title='2-3 PM', location=location.top, text='2-3 PM\nNY', color=NA(Color), textcolor=col_SB, offset=tfs)
    plotchar(high if targetHi else na, 'target high', '•', location.abovebar, color=cResLine, size=size.small)
    plotchar(low if targetLo else na, 'target low', '•', location.belowbar, color=cSupLine, size=size.small)
    if barstate.islast:
        if timeframe.in_seconds(timeframe.period) > 15 * 60:
            table.cell(tab, 0, 0, text='Please use a timeframe <= 15 minutes', text_color=color.new('#FF0000'))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
