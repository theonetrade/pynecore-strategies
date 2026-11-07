"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_loop, pine_range
from pynecore.core.pine_method import method, method_call
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    alert, array, bar_index, barstate, box, close, color, currency, high,
    input, label, line, linefill, low, math, max_bars_back, na, nz, open, script, size, strategy,
    string, ta, time, yloc
)
from pynecore.types import Box, Color, Label, Line, LineFill, NA, Persistent, Series


@udt
class ZZ:
    d: list[int] = na(list)
    x: list[int] = na(list)
    y: list[float] = na(list)
    l: list[Line] = na(list)


@udt
class Ewave:
    l1: Line = na(Line)
    l2: Line = na(Line)
    l3: Line = na(Line)
    l4: Line = na(Line)
    l5: Line = na(Line)
    b1: Label = na(Label)
    b2: Label = na(Label)
    b3: Label = na(Label)
    b4: Label = na(Label)
    b5: Label = na(Label)
    on: bool = na(bool)
    br: bool = na(bool)
    dir: int = na(int)
    lA: Line = na(Line)
    lB: Line = na(Line)
    lC: Line = na(Line)
    bA: Label = na(Label)
    bB: Label = na(Label)
    bC: Label = na(Label)
    next: bool = False
    lb: Label = na(Label)
    bx: Box = na(Box)


@udt
class fibL:
    wave1_0_500: Line = na(Line)
    wave1_0_618: Line = na(Line)
    wave1_0_764: Line = na(Line)
    wave1_0_854: Line = na(Line)
    wave1_pole_: Line = na(Line)
    l_fill_: LineFill = na(LineFill)
    _break_: bool = na(bool)


@script.strategy('Elliott Wave with Supertrend Exit - Strategy [presentTrading]', overlay=True, precision=3, default_qty_type=strategy.percent_of_equity, commission_value=0.1, commission_type=strategy.commission.percent, slippage=1, currency=currency.USD, default_qty_value=10, initial_capital=10000, margin_long=0, margin_short=0, close_by_id=True)
def main(
    tradingDirection=input.string('Both', 'Trading Direction', options=('Long', 'Short', 'Both')),
    i_hi=input.string('high', title='', group='source [high - low]', inline='hl', options=('high', 'close', 'max open/close')),
    i_lo=input.string('low', title='', group='source [high - low]', inline='hl', options=('low', 'close', 'min open/close')),
    s1=input.bool(True, title='', group='ZigZag', inline='1'),
    len1=input.int(4, title='  1 Length', group='ZigZag', inline='1', minval=1),
    col1=input.color(color.red, title='', group='ZigZag', inline='1'),
    STMultiplier=input.float(3, title='Supertrend Multiplier', group='Exit condition: Supertrend'),
    STLength=input.int(10, title='Supertrend Length', group='Exit condition: Supertrend'),
    stopLossPercentage=input.float(10, title='Stop Loss Percentage (%)', group='Stoploss: Fix percentage'),
    i_500=input.float(0.5, title='           level 1', group='Fibonacci values', minval=0, maxval=1, step=0.01),
    i_618=input.float(0.618, title='           level 2', group='Fibonacci values', minval=0, maxval=1, step=0.01),
    i_764=input.float(0.764, title='           level 3', group='Fibonacci values', minval=0, maxval=1, step=0.01),
    i_854=input.float(0.854, title='           level 4', group='Fibonacci values', minval=0, maxval=1, step=0.01),
    shZZ=input.bool(False, title='', group='show ZZ', inline='zz')
):
    hi: Series = high if i_hi == 'high' else close if i_hi == 'close' else math.max(open, close)
    lo: Series = low if i_lo == 'low' else close if i_hi == 'close' else math.min(open, close)
    def in_out(aZZ, d__00000020__, x1, y1, x2, y2, col):
        method_call('unshift', aZZ.d, d__00000020__)
        method_call('unshift', aZZ.x, x2)
        method_call('unshift', aZZ.y, y2)
        method_call('pop', aZZ.d)
        method_call('pop', aZZ.x)
        method_call('pop', aZZ.y)
        __block_result__ = na
        if shZZ:
            method_call('unshift', aZZ.l, line.new(x1, y1, x2, y2, color=col))
            __block_result__ = method_call('delete', method_call('pop', aZZ.l))
        return __block_result__

    @method
    def isSame(gEW: Ewave, _1x, _2x, _3x, _4x):
        t1 = _1x == line.get_x1(gEW.l1)
        t2 = _2x == line.get_x1(gEW.l2)
        t3 = _3x == line.get_x1(gEW.l3)
        t4 = _4x == line.get_x1(gEW.l4)
        return t1 and t2 and t3 and t4

    @method
    def isSame2(gEW: Ewave, _1x, _2x, _3x):
        t1 = _1x == line.get_x2(gEW.l3)
        t2 = _2x == line.get_x2(gEW.l4)
        t3 = _3x == line.get_x2(gEW.l5)
        return t1 and t2 and t3

    @method
    def dot(gEW: Ewave):
        line.set_style(gEW.l1, line.style_dotted)
        line.set_style(gEW.l2, line.style_dotted)
        line.set_style(gEW.l3, line.style_dotted)
        line.set_style(gEW.l4, line.style_dotted)
        line.set_style(gEW.l5, line.style_dotted)
        label.set_textcolor(gEW.b1, NA(Color))
        label.set_textcolor(gEW.b2, NA(Color))
        label.set_textcolor(gEW.b3, NA(Color))
        label.set_textcolor(gEW.b4, NA(Color))
        label.set_textcolor(gEW.b5, NA(Color))
        gEW.on = False
        return gEW.on

    @method
    def dash(gEW: Ewave):
        line.set_style(gEW.lA, line.style_dashed)
        line.set_style(gEW.lB, line.style_dashed)
        line.set_style(gEW.lC, line.style_dashed)
        label.set_textcolor(gEW.bA, NA(Color))
        label.set_textcolor(gEW.bB, NA(Color))
        label.set_textcolor(gEW.bC, NA(Color))
        box.set_bgcolor(gEW.bx, NA(Color))
        return box.set_border_color(gEW.bx, NA(Color))

    @method
    def sol_dot(nFibL: fibL, sol_dot__00000043__, col):
        style = line.style_dotted if sol_dot__00000043__ == 'dot' else line.style_solid if sol_dot__00000043__ == 'sol' else line.style_dashed
        line.set_style(nFibL.wave1_0_500, style)
        line.set_style(nFibL.wave1_0_618, style)
        line.set_style(nFibL.wave1_0_764, style)
        line.set_style(nFibL.wave1_0_854, style)
        return linefill.set_color(nFibL.l_fill_, col)

    @method
    def set(nFibL: fibL, x1: int, x2: int, max_500: float, max_618: float, max_764: float, max_854: float, y2: float):
        line.set_xy1(nFibL.wave1_0_500, x1, max_500)
        line.set_xy2(nFibL.wave1_0_500, x2, max_500)
        line.set_xy1(nFibL.wave1_0_618, x1, max_618)
        line.set_xy2(nFibL.wave1_0_618, x2, max_618)
        line.set_xy1(nFibL.wave1_0_764, x1, max_764)
        line.set_xy2(nFibL.wave1_0_764, x2, max_764)
        line.set_xy1(nFibL.wave1_0_854, x1, max_854)
        line.set_xy2(nFibL.wave1_0_854, x2, max_854)
        line.set_xy1(nFibL.wave1_pole_, x1, y2)
        line.set_xy2(nFibL.wave1_pole_, x1, max_854)
        method_call('set_xy1', linefill.get_line1(nFibL.l_fill_), x1, max_764)
        method_call('set_xy2', linefill.get_line1(nFibL.l_fill_), x2, max_764)
        method_call('set_xy1', linefill.get_line2(nFibL.l_fill_), x1, max_854)
        return method_call('set_xy2', linefill.get_line2(nFibL.l_fill_), x2, max_854)

    @method
    def setNa(nFibL: fibL):
        line.set_xy1(nFibL.wave1_0_500, na, na)
        line.set_xy2(nFibL.wave1_0_500, na, na)
        line.set_xy1(nFibL.wave1_0_618, na, na)
        line.set_xy2(nFibL.wave1_0_618, na, na)
        line.set_xy1(nFibL.wave1_0_764, na, na)
        line.set_xy2(nFibL.wave1_0_764, na, na)
        line.set_xy1(nFibL.wave1_0_854, na, na)
        line.set_xy2(nFibL.wave1_0_854, na, na)
        line.set_xy1(nFibL.wave1_pole_, na, na)
        line.set_xy2(nFibL.wave1_pole_, na, na)
        return linefill.set_color(nFibL.l_fill_, NA(Color))

    def draw(enabled, left, col, n):
        __hist_lo__: Series = lo[0]
        __hist_hi__: Series = hi[0]
        longEntry: bool = False
        shortEntry: bool = False
        max_bars_back(time, 4000)
        dir: Persistent[int] = na(int)
        x1: Persistent[int] = na(int)
        y1: Persistent[float] = na(float)
        x2: Persistent[int] = na(int)
        y2: Persistent[float] = na(float)
        gEW: Persistent[Ewave] = na(Ewave)
        last_0x: Persistent[int] = na(int)
        last_0y: Persistent[float] = na(float)
        last_6x: Persistent[int] = na(int)
        last_6y: Persistent[float] = na(float)
        if enabled:
            nFibL: Persistent[fibL] = fibL(wave1_0_500=line.new(na, na, na, na, color=color.new(col, 50), style=line.style_solid), wave1_0_618=line.new(na, na, na, na, color=color.new(col, 38), style=line.style_solid), wave1_0_764=line.new(na, na, na, na, color=color.new(col, 24), style=line.style_solid), wave1_0_854=line.new(na, na, na, na, color=color.new(col, 15), style=line.style_solid), wave1_pole_=line.new(na, na, na, na, color=color.new(col, 50), style=line.style_dashed), l_fill_=linefill.new(line.new(na, na, na, na, color=NA(Color)), line.new(na, na, na, na, color=NA(Color)), color=NA(Color)), _break_=na)
            aZZ: Persistent[ZZ] = ZZ(array.new_int(), array.new_int(), array.new_float(), array.new_line())
            aEW: Persistent[list[Ewave]] = array.new(0, NA(Ewave))
            if barstate.isfirst:
                array.unshift(aEW, Ewave())
                for i in pine_range(0, 10, 1):
                    array.unshift(aZZ.d, 0)
                    array.unshift(aZZ.x, 0)
                    array.unshift(aZZ.y, 0)
                    array.unshift(aZZ.l, line.new(na, na, na, na) if shZZ else na)
            sz = array.size(aZZ.d)
            x2 = bar_index - 1
            ph = ta.pivothigh(hi, left, 1)
            pl = ta.pivotlow(lo, left, 1)
            t = '\n\n' if n == 2 else '\n' if n == 1 else ''
            if not na(ph):
                gEW = array.get(aEW, 0)
                dir = array.get(aZZ.d, 0)
                x1 = array.get(aZZ.x, 0)
                y1 = array.get(aZZ.y, 0)
                y2 = nz(__hist_hi__[1])
                if dir < 1:
                    in_out(aZZ, 1, x1, y1, x2, y2, col)
                else:
                    if dir == 1 and ph > y1:
                        array.set(aZZ.x, 0, x2)
                        array.set(aZZ.y, 0, y2)
                        if shZZ:
                            method_call('set_xy2', array.get(aZZ.l, 0), x2, y2)
                _6x = x2
                _6y = y2
                _5x = array.get(aZZ.x, 1)
                _5y = array.get(aZZ.y, 1)
                _4x = array.get(aZZ.x, 2)
                _4y = array.get(aZZ.y, 2)
                _3x = array.get(aZZ.x, 3)
                _3y = array.get(aZZ.y, 3)
                _2x = array.get(aZZ.x, 4)
                _2y = array.get(aZZ.y, 4)
                _1x = array.get(aZZ.x, 5)
                _1y = array.get(aZZ.y, 5)
                _W5 = _6y - _5y
                _W3 = _4y - _3y
                _W1 = _2y - _1y
                min = math.min(_W1, _W3, _W5)
                isWave = _W3 != min and _6y > _4y and (_3y > _1y) and (_5y > _2y)
                same = isSame(gEW, _1x, _2x, _3x, _4x)
                if isWave:
                    if same:
                        line.set_xy2(gEW.l5, _6x, _6y)
                        label.set_xy(gEW.b5, _6x, _6y)
                    else:
                        tx: str = ''
                        if _2x == method_call('get_x', array.get(aEW, 0).b5):
                            tx = '(5) (1)'
                            method_call('set_text', array.get(aEW, 0).b5, '')
                        else:
                            tx = '(1)'
                        wave: Ewave = Ewave(l1=line.new(_1x, _1y, _2x, _2y, color=col, style=line.style_solid), l2=line.new(_2x, _2y, _3x, _3y, color=col, style=line.style_solid), l3=line.new(_3x, _3y, _4x, _4y, color=col, style=line.style_solid), l4=line.new(_4x, _4y, _5x, _5y, color=col, style=line.style_solid), l5=line.new(_5x, _5y, _6x, _6y, color=col, style=line.style_solid), b1=label.new(_2x, _2y, text=tx + t, textcolor=col, color=NA(Color), style=label.style_label_down), b2=label.new(_3x, _3y, text=t + '(2)', textcolor=col, color=NA(Color), style=label.style_label_up), b3=label.new(_4x, _4y, text='(3)' + t, textcolor=col, color=NA(Color), style=label.style_label_down), b4=label.new(_5x, _5y, text=t + '(4)', textcolor=col, color=NA(Color), style=label.style_label_up), b5=label.new(_6x, _6y, text='(5)' + t, textcolor=col, color=NA(Color), style=label.style_label_down), on=True, br=False, dir=1)
                        array.unshift(aEW, wave)
                        nFibL._break_ = False
                        alert('New EW Motive Bullish Pattern found', alert.freq_once_per_bar_close)
                if not isWave:
                    if same and gEW.on == True:
                        dot(gEW)
                        alert('Invalidated EW Motive Bullish Pattern', alert.freq_once_per_bar_close)
                getEW = array.get(aEW, 0)
                last_0x = method_call('get_x1', getEW.l1)
                last_0y = method_call('get_y1', getEW.l1)
                last_6x = method_call('get_x2', getEW.l5)
                last_6y = method_call('get_y2', getEW.l5)
                diff = math.abs(last_6y - last_0y)
                if getEW.dir == -1:
                    getX = method_call('get_x2', getEW.l5)
                    getY = method_call('get_y2', getEW.l5)
                    isSame2__000000dd__ = isSame2(getEW, _1x, _2x, _3x)
                    isValid = _3x == getX and _6y < getY + diff * i_854 and (_4y < getY + diff * i_854) and (_5y > getY)
                    if isValid:
                        width = _6x - _2x
                        if isSame2__000000dd__ and method_call('get_x', getEW.bA) > _3x:
                            method_call('set_xy1', getEW.lC, _5x, _5y)
                            method_call('set_xy2', getEW.lC, _6x, _6y)
                            method_call('set_xy', getEW.bC, _6x, _6y)
                            method_call('set_lefttop', getEW.bx, _6x, _6y)
                            method_call('set_right', getEW.bx, _6x + width)
                        else:
                            getEW.lA = line.new(_3x, _3y, _4x, _4y, color=col)
                            getEW.bA = label.new(_4x, _4y, text='(a)' + t, textcolor=col, color=NA(Color), style=label.style_label_down)
                            getEW.lB = line.new(_4x, _4y, _5x, _5y, color=col)
                            getEW.bB = label.new(_5x, _5y, text=t + '(b)', textcolor=col, color=NA(Color), style=label.style_label_up)
                            getEW.lC = line.new(_5x, _5y, _6x, _6y, color=col)
                            getEW.bC = label.new(_6x, _6y, text='(c)' + t, textcolor=col, color=NA(Color), style=label.style_label_down)
                            getEW.bx = box.new(_6x, _6y, _6x + width, _4y, bgcolor=color.new(col, 93), border_color=color.new(col, 65))
                            alert('New EW Corrective Bullish Pattern found', alert.freq_once_per_bar_close)
                    else:
                        if isSame2__000000dd__ and method_call('get_x', getEW.bA) > _3x:
                            dash(getEW)
                            alert('Invalidated EW Corrective Bullish Pattern', alert.freq_once_per_bar_close)
                if getEW.dir == 1:
                    if _5x == method_call('get_x', getEW.bC) and _6y > method_call('get_y', getEW.b5) and (getEW.next == False):
                        getEW.next = True
                        getEW.lb = label.new(_6x, _6y, style=label.style_circle, color=color.new(col, 65), yloc=yloc.abovebar, size=size.tiny)
                        alert('Possible new start of EW Motive Bullish Wave', alert.freq_once_per_bar_close)
                if isWave and getEW.dir == 1:
                    longEntry = True
            if not na(pl):
                gEW = array.get(aEW, 0)
                dir = array.get(aZZ.d, 0)
                x1 = array.get(aZZ.x, 0)
                y1 = array.get(aZZ.y, 0)
                y2 = nz(__hist_lo__[1])
                if dir > -1:
                    in_out(aZZ, -1, x1, y1, x2, y2, col)
                else:
                    if dir == -1 and pl < y1:
                        array.set(aZZ.x, 0, x2)
                        array.set(aZZ.y, 0, y2)
                        if shZZ:
                            method_call('set_xy2', array.get(aZZ.l, 0), x2, y2)
                _6x = x2
                _6y = y2
                _5x = array.get(aZZ.x, 1)
                _5y = array.get(aZZ.y, 1)
                _4x = array.get(aZZ.x, 2)
                _4y = array.get(aZZ.y, 2)
                _3x = array.get(aZZ.x, 3)
                _3y = array.get(aZZ.y, 3)
                _2x = array.get(aZZ.x, 4)
                _2y = array.get(aZZ.y, 4)
                _1x = array.get(aZZ.x, 5)
                _1y = array.get(aZZ.y, 5)
                _W5 = _5y - _6y
                _W3 = _3y - _4y
                _W1 = _1y - _2y
                min = math.min(_W1, _W3, _W5)
                isWave = _W3 != min and _4y > _6y and (_1y > _3y) and (_2y > _5y)
                same = isSame(gEW, _1x, _2x, _3x, _4x)
                if isWave:
                    if same:
                        line.set_xy2(gEW.l5, _6x, _6y)
                        label.set_xy(gEW.b5, _6x, _6y)
                    else:
                        tx: str = ''
                        if _2x == method_call('get_x', array.get(aEW, 0).b5):
                            tx = '(5) (1)'
                            method_call('set_text', array.get(aEW, 0).b5, '')
                        else:
                            tx = '(1)'
                        wave: Ewave = Ewave(l1=line.new(_1x, _1y, _2x, _2y, color=col, style=line.style_solid), l2=line.new(_2x, _2y, _3x, _3y, color=col, style=line.style_solid), l3=line.new(_3x, _3y, _4x, _4y, color=col, style=line.style_solid), l4=line.new(_4x, _4y, _5x, _5y, color=col, style=line.style_solid), l5=line.new(_5x, _5y, _6x, _6y, color=col, style=line.style_solid), b1=label.new(_2x, _2y, text=t + tx, textcolor=col, color=NA(Color), style=label.style_label_up), b2=label.new(_3x, _3y, text='(2)' + t, textcolor=col, color=NA(Color), style=label.style_label_down), b3=label.new(_4x, _4y, text=t + '(3)', textcolor=col, color=NA(Color), style=label.style_label_up), b4=label.new(_5x, _5y, text='(4)' + t, textcolor=col, color=NA(Color), style=label.style_label_down), b5=label.new(_6x, _6y, text=t + '(5)', textcolor=col, color=NA(Color), style=label.style_label_up), on=True, br=False, dir=-1)
                        array.unshift(aEW, wave)
                        nFibL._break_ = False
                        alert('New EW Motive Bearish Pattern found', alert.freq_once_per_bar_close)
                if not isWave:
                    if same and gEW.on == True:
                        dot(gEW)
                        alert('Invalidated EW Motive Bearish Pattern', alert.freq_once_per_bar_close)
                getEW = array.get(aEW, 0)
                last_0x = method_call('get_x1', getEW.l1)
                last_0y = method_call('get_y1', getEW.l1)
                last_6x = method_call('get_x2', getEW.l5)
                last_6y = method_call('get_y2', getEW.l5)
                diff = math.abs(last_6y - last_0y)
                if getEW.dir == 1:
                    getX = method_call('get_x2', getEW.l5)
                    getY = method_call('get_y2', getEW.l5)
                    isSame2__00000140__ = isSame2(getEW, _1x, _2x, _3x)
                    isValid = _3x == getX and _6y > getY - diff * i_854 and (_4y > getY - diff * i_854) and (_5y < getY)
                    if isValid:
                        width = _6x - _2x
                        if isSame2__00000140__ and method_call('get_x', getEW.bA) > _3x:
                            method_call('set_xy1', getEW.lC, _5x, _5y)
                            method_call('set_xy2', getEW.lC, _6x, _6y)
                            method_call('set_xy', getEW.bC, _6x, _6y)
                            method_call('set_lefttop', getEW.bx, _6x, _6y)
                            method_call('set_right', getEW.bx, _6x + width)
                        else:
                            getEW.lA = line.new(_3x, _3y, _4x, _4y, color=col)
                            getEW.bA = label.new(_4x, _4y, text=t + '(a)', textcolor=col, color=NA(Color), style=label.style_label_up)
                            getEW.lB = line.new(_4x, _4y, _5x, _5y, color=col)
                            getEW.bB = label.new(_5x, _5y, text='(b)' + t, textcolor=col, color=NA(Color), style=label.style_label_down)
                            getEW.lC = line.new(_5x, _5y, _6x, _6y, color=col)
                            getEW.bC = label.new(_6x, _6y, text=t + '(c)', textcolor=col, color=NA(Color), style=label.style_label_up)
                            getEW.bx = box.new(_6x, _6y, _6x + width, _4y, bgcolor=color.new(col, 93), border_color=color.new(col, 65))
                            alert('New EW Corrective Bearish Pattern found', alert.freq_once_per_bar_close)
                    else:
                        if isSame2__00000140__ and method_call('get_x', getEW.bA) > _3x:
                            dash(getEW)
                            alert('Invalidated EW Corrective Bullish Pattern', alert.freq_once_per_bar_close)
                if getEW.dir == -1:
                    if _5x == method_call('get_x', getEW.bC) and _6y < method_call('get_y', getEW.b5) and (getEW.next == False):
                        getEW.next = True
                        getEW.lb = label.new(_6x, _6y, style=label.style_circle, color=color.new(col, 65), yloc=yloc.belowbar, size=size.tiny)
                        alert('Possible new start of EW Motive Bearish Wave', alert.freq_once_per_bar_close)
                if isWave and getEW.dir == -1:
                    shortEntry = True
            if array.size(aEW) > 0:
                gEW = array.get(aEW, 0)
                if gEW.dir == 1:
                    if ta.crossunder(low, box.get_bottom(gEW.bx)) and bar_index <= box.get_right(gEW.bx):
                        label.new(bar_index, low, yloc=yloc.belowbar, style=label.style_xcross, color=color.red, size=size.tiny)
                else:
                    if ta.crossover(high, box.get_top(gEW.bx)) and bar_index <= box.get_right(gEW.bx):
                        label.new(bar_index, high, yloc=yloc.abovebar, style=label.style_xcross, color=color.red, size=size.tiny)
            if barstate.islast:
                getEW = array.get(aEW, 0)
                if array.size(aEW) > 1:
                    getEW1 = array.get(aEW, 1)
                    last_0x = method_call('get_x1', getEW.l1)
                    last_0y = method_call('get_y1', getEW.l1)
                    last_6x = method_call('get_x2', getEW.l5)
                    last_6y = method_call('get_y2', getEW.l5)
                    diff = math.abs(last_6y - last_0y)
                    _500 = diff * i_500
                    _618 = diff * i_618
                    _764 = diff * i_764
                    _854 = diff * i_854
                    bull = getEW.dir == 1
                    if getEW.on == False or method_call('get_x', getEW.bC) > method_call('get_x', getEW.b5):
                        setNa(nFibL)
                    else:
                        max_500 = last_6y + (-1 if bull else 1) * _500
                        max_618 = last_6y + (-1 if bull else 1) * _618
                        max_764 = last_6y + (-1 if bull else 1) * _764
                        max_854 = last_6y + (-1 if bull else 1) * _854
                        set(nFibL, last_6x, bar_index + 10, max_500, max_618, max_764, max_854, last_6y)
                    if method_call('get_x', getEW.b2) == method_call('get_x', getEW1.bC):
                        method_call('set_textcolor', getEW.b1, NA(Color))
                        method_call('set_textcolor', getEW.b2, NA(Color))
                        strB = method_call('get_text', getEW1.bB)
                        strC = method_call('get_text', getEW1.bC)
                        strB_ = string.replace(strB, '(b)', '(b) (1)', 0)
                        strC_ = string.replace(strC, '(c)', '(c) (2)', 0)
                        method_call('set_text', getEW1.bB, strB_)
                        method_call('set_text', getEW1.bC, strC_)
                getP_854 = line.get_y1(nFibL.wave1_0_854)
                __loop_2__ = pine_loop(0, 1)
                while __loop_2__.step(bar_index - line.get_x1(nFibL.wave1_0_854)):
                    i = __loop_2__.value
                    if getEW.dir == -1:
                        if high[i] > getP_854:
                            nFibL._break_ = True
                            break
                    else:
                        if low[i] < getP_854:
                            nFibL._break_ = True
                            break
                __switch_2__ = nFibL._break_
                if __switch_2__ == True:
                    sol_dot(nFibL, 'dot', color.new(color.red, 95))
                elif __switch_2__ == False:
                    sol_dot(nFibL, 'sol', color.new(color.lime, 95))
                else:
                    line.set_xy1(nFibL.wave1_0_500, na, na)
                    line.set_xy2(nFibL.wave1_0_500, na, na)
                    line.set_xy1(nFibL.wave1_0_618, na, na)
                    line.set_xy2(nFibL.wave1_0_618, na, na)
                    line.set_xy1(nFibL.wave1_0_764, na, na)
                    line.set_xy2(nFibL.wave1_0_764, na, na)
                    line.set_xy1(nFibL.wave1_0_854, na, na)
                    line.set_xy2(nFibL.wave1_0_854, na, na)
                    line.set_xy1(nFibL.wave1_pole_, na, na)
                    line.set_xy2(nFibL.wave1_pole_, na, na)
                    linefill.set_color(nFibL.l_fill_, NA(Color))
            if array.size(aEW) > 15:
                pop = array.pop(aEW)
                method_call('delete', pop.l1)
                method_call('delete', pop.b1)
                method_call('delete', pop.l2)
                method_call('delete', pop.b2)
                method_call('delete', pop.l3)
                method_call('delete', pop.b3)
                method_call('delete', pop.l4)
                method_call('delete', pop.b4)
                method_call('delete', pop.l5)
                method_call('delete', pop.b5)
                method_call('delete', pop.lA)
                method_call('delete', pop.bA)
                method_call('delete', pop.lB)
                method_call('delete', pop.bB)
                method_call('delete', pop.lC)
                method_call('delete', pop.bC)
                method_call('delete', pop.lb)
                method_call('delete', pop.bx)
        return (longEntry, shortEntry)

    draw(s1, len1, col1, 0)
    longEntry1, shortEntry1 = draw(s1, len1, col1, 0)
    longStopLossLevel = close * (1 - stopLossPercentage / 100)
    shortStopLossLevel = close * (1 + stopLossPercentage / 100)
    if shortEntry1 and (tradingDirection == 'Long' or tradingDirection == 'Both'):
        strategy.entry('Buy', strategy.long)
        strategy.exit('Exit Long', 'Buy', stop=longStopLossLevel)
    if longEntry1 and (tradingDirection == 'Short' or tradingDirection == 'Both'):
        strategy.entry('Sell', strategy.short)
        strategy.exit('Exit Short', 'Sell', stop=shortStopLossLevel)
    supertrend, direction = ta.supertrend(STMultiplier, STLength)
    prevDirection: Persistent[float] = na(float)
    longExit: bool = False
    shortExit: bool = False
    if na(prevDirection):
        prevDirection = direction
    else:
        if direction != prevDirection:
            longExit = prevDirection < 0
            shortExit = prevDirection > 0
            prevDirection = direction
    if longExit and (tradingDirection == 'Long' or tradingDirection == 'Both'):
        strategy.close('Buy')
    if shortExit and (tradingDirection == 'Short' or tradingDirection == 'Both'):
        strategy.close('Sell')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
