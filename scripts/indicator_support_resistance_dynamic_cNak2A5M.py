"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    alertcondition, array, bar_index, close, color, display, extend, high,
    input, label, line, location, low, math, na, nz, plot, plotshape, script, shape, string, ta
)
from pynecore.types import Label, Line, Persistent, Series


@script.indicator('Support Resistance - Dynamic', overlay=True, max_bars_back=600, na_bool=True)
def main(
    rb=input.int(10, title='Period for Pivot Points', minval=10),
    prd=input.int(284, title='Loopback Period', minval=100, maxval=500),
    nump=input.int(2, title='S/R strength', minval=1),
    ChannelW=input.int(10, title='Channel Width %', minval=5),
    label_location=input.int(10, title='Label Location +-', tooltip='0 means last bar. for example if you set it -5 then label is shown on last 5. bar. + means future bars'),
    linestyle=input.string('Dashed', title='Line Style', options=('Solid', 'Dotted', 'Dashed')),
    LineColor=input(color.blue, title='Line Color'),
    drawhl=input(True, title='Draw Highest/Lowest Pivots in Period'),
    showpp=input(False, title='Show Point Points')
):
    ph: Series = ta.pivothigh(rb, rb)
    pl: Series = ta.pivotlow(rb, rb)
    plotshape(cast_bool(ph) and showpp, text='PH', style=shape.labeldown, color=color.new(color.white, 100), textcolor=color.new(color.red, 0), location=location.abovebar, offset=-rb)
    plotshape(cast_bool(pl) and showpp, text='PL', style=shape.labelup, color=color.new(color.white, 100), textcolor=color.new(color.lime, 0), location=location.belowbar, offset=-rb)
    sr_levels: list[float] = array.new_float(21, na)
    prdhighest = ta.highest(prd)
    prdlowest = ta.lowest(prd)
    cwidth = (prdhighest - prdlowest) * ChannelW / 100
    aas: list[bool] = array.new_bool(41, True)
    u1: Series[float] = 0.0
    u1 = nz(u1[1])
    d1: Series[float] = 0.0
    d1 = nz(d1[1])
    highestph: Series[float] = 0.0
    lowestpl: Series[float] = 0.0
    highestph = highestph[1]
    lowestpl = lowestpl[1]
    if cast_bool(ph) or cast_bool(pl):
        for x in pine_range(0, array.size(sr_levels) - 1, 1):
            array.set(sr_levels, x, na)
        highestph = prdlowest
        lowestpl = prdhighest
        countpp: int = 0
        for x in pine_range(0, prd, 1):
            if na(close[x]):
                break
            if not na(ph[x]) or not na(pl[x]):
                highestph = math.max(highestph, nz(ph[x], prdlowest), nz(pl[x], prdlowest))
                lowestpl = math.min(lowestpl, nz(ph[x], prdhighest), nz(pl[x], prdhighest))
                countpp = countpp + 1
                if countpp > 40:
                    break
                if array.get(aas, countpp):
                    upl = (high[x + rb] if cast_bool(ph[x]) else low[x + rb]) + cwidth
                    dnl = (high[x + rb] if cast_bool(ph[x]) else low[x + rb]) - cwidth
                    u1 = upl if countpp == 1 else u1
                    d1 = dnl if countpp == 1 else d1
                    tmp: list[bool] = array.new_bool(41, True)
                    cnt: int = 0
                    tpoint: int = 0
                    for xx in pine_range(0, prd, 1):
                        if na(close[xx]):
                            break
                        if not na(ph[xx]) or not na(pl[xx]):
                            chg: bool = False
                            cnt = cnt + 1
                            if cnt > 40:
                                break
                            if array.get(aas, cnt):
                                if not na(ph[xx]):
                                    if high[xx + rb] <= upl and high[xx + rb] >= dnl:
                                        tpoint = tpoint + 1
                                        chg = True
                                if not na(pl[xx]):
                                    if low[xx + rb] <= upl and low[xx + rb] >= dnl:
                                        tpoint = tpoint + 1
                                        chg = True
                            if chg and cnt < 41:
                                array.set(tmp, cnt, False)
                    if tpoint >= nump:
                        for g in pine_range(0, 40, 1):
                            if not array.get(tmp, g):
                                array.set(aas, g, False)
                        if cast_bool(ph[x]) and countpp < 21:
                            array.set(sr_levels, countpp, high[x + rb])
                        if cast_bool(pl[x]) and countpp < 21:
                            array.set(sr_levels, countpp, low[x + rb])
    def setline(level):
        LineStyle = line.style_solid if linestyle == 'Solid' else line.style_dotted if linestyle == 'Dotted' else line.style_dashed
        _ret = line.new(bar_index - 1, level, bar_index, level, color=LineColor, width=2, style=LineStyle, extend=extend.both)
        return _ret

    if cast_bool(ph) or cast_bool(pl):
        highest_: Persistent[Line] = na(Line)
        lowest_: Persistent[Line] = na(Line)
        line.delete(highest_)
        line.delete(lowest_)
        if drawhl:
            highest_ = line.new(bar_index - 1, highestph, bar_index, highestph, color=color.blue, style=line.style_dashed, width=1, extend=extend.both)
            lowest_ = line.new(bar_index - 1, lowestpl, bar_index, lowestpl, color=color.blue, style=line.style_dashed, width=1, extend=extend.both)
        sr_lines: Persistent[list[Line]] = array.new_line(21, na)
        for x in pine_range(0, array.size(sr_lines) - 1, 1):
            line.delete(array.get(sr_lines, x))
            if cast_bool(array.get(sr_levels, x)):
                array.set(sr_lines, x, setline(array.get(sr_levels, x)))
    sr_levs: Persistent[list[float]] = array.new_float(21, na)
    if cast_bool(ph) or cast_bool(pl):
        for x in pine_range(0, array.size(sr_levs) - 1, 1):
            array.set(sr_levs, x, array.get(sr_levels, x))
    hlabel: Series[Label] = na(Label)
    llabel: Series[Label] = na(Label)
    label.delete(hlabel[1])
    label.delete(llabel[1])
    sr_labels: Persistent[list[Label]] = array.new_label(21, na)
    resistance_broken: bool = False
    support_broken: bool = False
    r_s_level: float = na(float)
    for x in pine_range(0, array.size(sr_labels) - 1, 1):
        label.delete(array.get(sr_labels, x))
        if cast_bool(array.get(sr_levs, x)):
            if close[1] <= array.get(sr_levs, x) and close > array.get(sr_levs, x):
                resistance_broken = True
                r_s_level = array.get(sr_levs, x)
            if close[1] >= array.get(sr_levs, x) and close < array.get(sr_levs, x):
                support_broken = True
                r_s_level = array.get(sr_levs, x)
            lab_loc = label.style_label_up if close >= array.get(sr_levs, x) else label.style_label_down
            array.set(sr_labels, x, label.new(x=bar_index + label_location, y=array.get(sr_levs, x), text=string.tostring(math.round_to_mintick(array.get(sr_levs, x))), color=color.lime, textcolor=color.black, style=lab_loc))
    hlabel = label.new(x=bar_index + label_location + math.round(math.sign(label_location)) * 20, y=highestph, text='Highest PH ' + string.tostring(highestph), color=color.silver, textcolor=color.black, style=label.style_label_down) if drawhl else na
    llabel = label.new(x=bar_index + label_location + math.round(math.sign(label_location)) * 20, y=lowestpl, text='Lowest PL ' + string.tostring(lowestpl), color=color.silver, textcolor=color.black, style=label.style_label_up) if drawhl else na
    plot(r_s_level, title='RS_level', display=display.none)
    alertcondition(resistance_broken, title='Resistance Broken', message='Resistance Broken, Close Price: {{close}}, Resistance level = {{plot("RS_level")}}')
    alertcondition(support_broken, title='Support Broken', message='Support Broken, Close Price: {{close}}, Support level = {{plot("RS_level")}}')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
