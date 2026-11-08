"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_bool
from pynecore.core.pine_method import method_call
from pynecore.lib import (
    alertcondition, array, barmerge, box, close, color, extend, high, input,
    line, location, low, math, na, open, plotshape, request, script, shape, size, syminfo, ta,
    time, timeframe, xloc
)
from pynecore.types import Box, Color, Line, Persistent, Series

g_SET: str = 'Settings'
g_RJ: str = 'Rejections'


@script.indicator('Inverse FVG with Rejections [TFO]', 'Inverse FVG [TFO]', True, na_bool=True)
def main(
    show_rfvg=input.bool(True, 'Show Regular FVG', inline='RFVG', group=g_SET),
    show_ifvg=input.bool(True, 'Show Inverse FVG', inline='IFVG', group=g_SET),
    extend_right=input.bool(True, 'Extend Boxes', group=g_SET),
    rfvg_color=input.color(color.new(color.new('#2962FF'), 60), '', inline='RFVG', group=g_SET),
    ifvg_color=input.color(color.new(color.new('#F23645'), 60), '', inline='IFVG', group=g_SET),
    tf=input.timeframe('', 'Timeframe', group=g_SET),
    disp_x=input.int(3, 'Displacement', minval=1, maxval=10, tooltip='Larger Displacement will require larger FVGs', group=g_SET),
    disp_limit=input.int(10, 'Display Limit', minval=1, maxval=50, tooltip='The maximum amount of FVGs and IFVGs to display', group=g_SET),
    session__ren__=input.session('0000-0000', 'Session', tooltip='FVGs will only be saved if they are created within this time period', group=g_SET),
    ps=input.int(1, 'Rejection Strength', tooltip='Larger values will require larger fractals/swing pivots to justify as rejections', group=g_RJ),
    show_rrj=input.bool(False, 'Regular FVG', inline='RRJ', tooltip='Show rejections made within regular FVGs', group=g_RJ),
    show_irj=input.bool(False, 'Inverse FVG', inline='IRJ', tooltip='Show rejections made within inverse FVGs', group=g_RJ),
    show_brj=input.bool(True, 'Regular + Inverse FVG', inline='BRJ', tooltip='Show rejections made within both regular and inverse FVGs', group=g_RJ),
    rrj_color=input.color(color.new('#2962FF'), '', inline='RRJ', group=g_RJ),
    irj_color=input.color(color.new('#F23645'), '', inline='IRJ', group=g_RJ),
    brj_color=input.color(color.black, '', inline='BRJ', group=g_RJ)
):
    t: Series = not na(time(tf, session__ren__, 'America/New_York'))
    o, h, l, c, ti = request.security(syminfo.tickerid, tf, (open[1], high[1], low[1], close[1], time[1]), lookahead=barmerge.lookahead_on, gaps=barmerge.gaps_off)
    tf_o: Persistent[list[float]] = array.new_float()
    tf_h: Persistent[list[float]] = array.new_float()
    tf_l: Persistent[list[float]] = array.new_float()
    tf_c: Persistent[list[float]] = array.new_float()
    tf_time: Persistent[list[int]] = array.new_int()
    tf_t: Persistent[list[bool]] = array.new_bool()
    reg_fvg: Persistent[list[Box]] = array.new_box()
    reg_fvg_ce: Persistent[list[Line]] = array.new_line()
    reg_fvg_side: Persistent[list[str]] = array.new_string()
    inv_fvg: Persistent[list[Box]] = array.new_box()
    inv_fvg_ce: Persistent[list[Line]] = array.new_line()
    inv_fvg_side: Persistent[list[str]] = array.new_string()
    reg_rj_bear: Series[bool] = False
    reg_rj_bull: Series[bool] = False
    inv_rj_bear: Series[bool] = False
    inv_rj_bull: Series[bool] = False
    def solid_color(x: Color):
        return color.new(x, 0)

    def avg_over(h: list[float], l: list[float], len: int):
        sum: float = 0.0
        for i in pine_range(0, len, 1):
            sum = sum + array.get(h, i) - array.get(l, i)
        result = sum / len
        return result

    tf_new: Persistent[bool] = False
    if timeframe.change(tf) and timeframe.in_seconds(tf) >= timeframe.in_seconds(timeframe.period):
        array.unshift(tf_o, o)
        array.unshift(tf_h, h)
        array.unshift(tf_l, l)
        array.unshift(tf_c, c)
        array.unshift(tf_t, t[1])
        array.unshift(tf_time, ti)
        tf_new = True
        if array.size(tf_o) > 300:
            array.pop(tf_o)
            array.pop(tf_h)
            array.pop(tf_l)
            array.pop(tf_c)
            array.pop(tf_t)
            array.pop(tf_time)
    if not extend_right:
        if array.size(reg_fvg) > 0:
            for i in pine_range(0, array.size(reg_fvg) - 1, 1):
                method_call('set_right', array.get(reg_fvg, i), time)
                method_call('set_x2', array.get(reg_fvg_ce, i), time)
        if array.size(inv_fvg) > 0:
            for i in pine_range(0, array.size(inv_fvg) - 1, 1):
                method_call('set_right', array.get(inv_fvg, i), time)
                method_call('set_x2', array.get(inv_fvg_ce, i), time)
    if array.size(tf_o) > 20 and tf_new:
        bull = array.get(tf_c, 1) > array.get(tf_o, 1)
        fvg = array.get(tf_h, 2) < array.get(tf_l, 0) and array.get(tf_l, 1) <= array.get(tf_h, 2) and (array.get(tf_h, 1) >= array.get(tf_l, 0)) if bull else array.get(tf_l, 2) > array.get(tf_h, 0) and array.get(tf_l, 1) <= array.get(tf_h, 0) and (array.get(tf_l, 2) <= array.get(tf_h, 1))
        fvg_len = array.get(tf_l, 0) - array.get(tf_h, 2) if bull else array.get(tf_l, 2) - array.get(tf_h, 0)
        atr_check = fvg_len > avg_over(tf_h, tf_l, 20) * disp_x / 10
        if array.get(tf_t, 2) and fvg and atr_check:
            top = array.get(tf_l, 0) if bull else array.get(tf_l, 2)
            bottom = array.get(tf_h, 2) if bull else array.get(tf_h, 0)
            array.unshift(reg_fvg, box.new(array.get(tf_time, 1), top, time, bottom, xloc=xloc.bar_time, extend=extend.right if extend_right else extend.none, bgcolor=rfvg_color if show_rfvg else na, border_color=na))
            array.unshift(reg_fvg_ce, line.new(array.get(tf_time, 1), math.avg(top, bottom), time, math.avg(top, bottom), xloc=xloc.bar_time, extend=extend.right if extend_right else extend.none, color=solid_color(rfvg_color) if show_rfvg else na, style=line.style_dashed))
            array.unshift(reg_fvg_side, 'bull' if bull else 'bear')
            tf_new = False
        if array.size(reg_fvg) > 0:
            for i in pine_range(array.size(reg_fvg) - 1, 0, 1):
                remove_bull = array.get(reg_fvg_side, i) == 'bull' and array.get(tf_c, 0) < method_call('get_bottom', array.get(reg_fvg, i))
                remove_bear = array.get(reg_fvg_side, i) == 'bear' and array.get(tf_c, 0) > method_call('get_top', array.get(reg_fvg, i))
                if remove_bull or remove_bear:
                    array.unshift(inv_fvg, box.copy(array.get(reg_fvg, i)))
                    array.unshift(inv_fvg_ce, line.copy(array.get(reg_fvg_ce, i)))
                    method_call('set_bgcolor', array.get(inv_fvg, 0), ifvg_color if show_ifvg else na)
                    method_call('set_color', array.get(inv_fvg_ce, 0), solid_color(ifvg_color) if show_ifvg else na)
                    box.delete(array.get(reg_fvg, i))
                    line.delete(array.get(reg_fvg_ce, i))
                    array.remove(reg_fvg, i)
                    array.remove(reg_fvg_ce, i)
                    array.remove(reg_fvg_side, i)
                    if remove_bear:
                        array.unshift(inv_fvg_side, 'inv bear')
                    elif remove_bull:
                        array.unshift(inv_fvg_side, 'inv bull')
            if array.size(reg_fvg) > disp_limit:
                box.delete(array.pop(reg_fvg))
                line.delete(array.pop(reg_fvg_ce))
                array.pop(reg_fvg_side)
        if array.size(inv_fvg) > 0:
            for i in pine_range(array.size(inv_fvg) - 1, 0, 1):
                remove_inv_bear = array.get(inv_fvg_side, i) == 'inv bear' and array.get(tf_c, 0) < method_call('get_bottom', array.get(inv_fvg, i))
                remove_inv_bull = array.get(inv_fvg_side, i) == 'inv bull' and array.get(tf_c, 0) > method_call('get_top', array.get(inv_fvg, i))
                if remove_inv_bear or remove_inv_bull:
                    box.delete(array.get(inv_fvg, i))
                    line.delete(array.get(inv_fvg_ce, i))
                    array.remove(inv_fvg, i)
                    array.remove(inv_fvg_ce, i)
                    array.remove(inv_fvg_side, i)
            if array.size(inv_fvg) > disp_limit:
                box.delete(array.pop(inv_fvg))
                line.delete(array.pop(inv_fvg_ce))
                array.pop(inv_fvg_side)
        if math.min(array.size(reg_fvg), array.size(inv_fvg)) > 0:
            for i in pine_range(0, array.size(reg_fvg) - 1, 1):
                _rrj_bear = cast_bool(ta.pivothigh(high, ps, ps)) and high[ps] >= method_call('get_bottom', array.get(reg_fvg, i)) and (high[ps] <= method_call('get_top', array.get(reg_fvg, i)))
                _rrj_bull = cast_bool(ta.pivotlow(low, ps, ps)) and low[ps] >= method_call('get_bottom', array.get(reg_fvg, i)) and (low[ps] <= method_call('get_top', array.get(reg_fvg, i)))
                if _rrj_bear:
                    reg_rj_bear = True
                if _rrj_bull:
                    reg_rj_bull = True
            for i in pine_range(0, array.size(inv_fvg) - 1, 1):
                _irj_bear = cast_bool(ta.pivothigh(high, ps, ps)) and high[ps] >= method_call('get_bottom', array.get(inv_fvg, i)) and (high[ps] <= method_call('get_top', array.get(inv_fvg, i)))
                _irj_bull = cast_bool(ta.pivotlow(low, ps, ps)) and low[ps] >= method_call('get_bottom', array.get(inv_fvg, i)) and (low[ps] <= method_call('get_top', array.get(inv_fvg, i)))
                if _irj_bear:
                    inv_rj_bear = True
                if _irj_bull:
                    inv_rj_bull = True
    plotshape(show_rrj and reg_rj_bear[1], color=rrj_color, size=size.small, location=location.abovebar, style=shape.triangledown)
    plotshape(show_rrj and reg_rj_bull[1], color=rrj_color, size=size.small, location=location.belowbar, style=shape.triangleup)
    plotshape(show_irj and inv_rj_bear[1], color=irj_color, size=size.small, location=location.abovebar, style=shape.triangledown)
    plotshape(show_irj and inv_rj_bull[1], color=irj_color, size=size.small, location=location.belowbar, style=shape.triangleup)
    plotshape(show_brj and reg_rj_bear[1] and inv_rj_bear[1], color=brj_color, size=size.small, location=location.abovebar, style=shape.triangledown)
    plotshape(show_brj and reg_rj_bull[1] and inv_rj_bull[1], color=brj_color, size=size.small, location=location.belowbar, style=shape.triangleup)
    alertcondition(show_rrj and (reg_rj_bear[1] or reg_rj_bull[1]), 'Any Regular FVG Rejection')
    alertcondition(show_rrj and reg_rj_bear[1], 'Regular FVG Bear Rejection')
    alertcondition(show_rrj and reg_rj_bull[1], 'Regular FVG Bull Rejection')
    alertcondition(show_irj and (inv_rj_bear[1] or inv_rj_bull[1]), 'Any Inverse FVG Rejection')
    alertcondition(show_irj and inv_rj_bear[1], 'Inverse FVG Bear Rejection')
    alertcondition(show_irj and inv_rj_bull[1], 'Inverse FVG Bull Rejection')
    alertcondition(show_brj and (reg_rj_bear[1] and inv_rj_bear[1] or (reg_rj_bull[1] and inv_rj_bull[1])), 'Any FVG + IFVG Rejection')
    alertcondition(show_brj and reg_rj_bear[1] and inv_rj_bear[1], 'FVG + IFVG Bear Rejection')
    alertcondition(show_brj and reg_rj_bull[1] and inv_rj_bull[1], 'FVG + IFVG Bull Rejection')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
