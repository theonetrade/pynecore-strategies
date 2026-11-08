"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    alert, bar_index, close, color, high, input, label, line, linefill,
    location, low, math, na, open, plotshape, script, shape, size, ta, time, timenow, xloc, yloc
)
from pynecore.types import Label, Persistent, Series


@script.indicator('Price action as in book: Fibonacci + Support/Resistant + Trendline', overlay=True, max_lines_count=500)
def main(
    buyonly=input.bool(title='Find entry  Long', defval=True, group='Set up Find entry'),
    sellonly=input.bool(title='Find entry Short', defval=False, group='Set up Find entry'),
    leftbars=input.int(10, minval=1, title='Pivot Detection: Left Bars', group='Set up Pivot High/Low'),
    rightbars=input.int(5, minval=1, title='Pivot Detection: Right Bars', group='Set up Pivot High/Low'),
    width_fibo=input.int(2, minval=1, title='Width Fibonacci levels', group='Custom Selection', inline='1'),
    width_sup_res=input.int(2, minval=1, title='Width Sup/Res levels', group='Custom Selection', inline='2'),
    width_trendline=input.int(2, minval=1, title='Width Trendline', group='Custom Selection'),
    extend_fibo=input.int(5, minval=1, title='Extention', group='Custom Selection', inline='1'),
    color_fibo_label=input.color(color.new(color.yellow, 0), title='Color Labels', group='Custom Selection', inline='1'),
    extend_sup_res=input.int(5, minval=1, title='Extention', group='Custom Selection', inline='2'),
    alert_input=input.string(title='Set alert Long Trade when price test', defval='Fibo 0.5', options=('Fibo 0.382', 'Fibo 0.5', 'Fibo 0.618', 'Fibo 0.786', 'Support Zone', 'Trendline'), group='Set up Alert'),
    alertshort_input=input.string(title='Set alert Short Trade when price test', defval='Fibo 0.5', options=('Fibo 0.382', 'Fibo 0.5', 'Fibo 0.618', 'Fibo 0.786', 'Resistant Zone', 'Trendline'), group='Set up Alert')
):
    ph = ta.pivothigh(high, leftbars, rightbars)
    pl = ta.pivotlow(low, leftbars, rightbars)
    phvalue1 = ta.valuewhen(cast_bool(ph), high[rightbars], 0)
    phbar1 = ta.valuewhen(cast_bool(ph), bar_index[rightbars], 0)
    phv1low = ta.valuewhen(cast_bool(ph), close[rightbars] if close[rightbars] > open[rightbars] else open[rightbars], 0)
    phvalue2 = ta.valuewhen(cast_bool(ph), high[rightbars], 1)
    phbar2 = ta.valuewhen(cast_bool(ph), bar_index[rightbars], 1)
    phv2low = ta.valuewhen(cast_bool(ph), close[rightbars] if close[rightbars] > open[rightbars] else open[rightbars], 1)
    phbar3 = ta.valuewhen(cast_bool(ph), bar_index[rightbars], 2)
    phvalue3 = ta.valuewhen(cast_bool(ph), high[rightbars], 2)
    plvalue1 = ta.valuewhen(cast_bool(pl), low[rightbars], 0)
    plbar1 = ta.valuewhen(cast_bool(pl), bar_index[rightbars], 0)
    plv1low = ta.valuewhen(cast_bool(pl), close[rightbars] if close[rightbars] < open[rightbars] else open[rightbars], 0)
    plvalue2 = ta.valuewhen(cast_bool(pl), low[rightbars], 1)
    plbar2 = ta.valuewhen(cast_bool(pl), bar_index[rightbars], 1)
    plbar3 = ta.valuewhen(cast_bool(pl), bar_index[rightbars], 2)
    plv2low = ta.valuewhen(cast_bool(pl), close[rightbars] if close[rightbars] < open[rightbars] else open[rightbars], 1)
    plvalue3 = ta.valuewhen(cast_bool(pl), low[rightbars], 2)
    plotshape(ph, style=shape.diamond, location=location.abovebar, color=color.new(color.red, 0), title='Pivot High', offset=-rightbars)
    plotshape(pl, style=shape.diamond, location=location.belowbar, color=color.new(color.green, 0), title='Pivot Low', offset=-rightbars)
    def _slope(x1, x2, y1, y2):
        m = (y2 - y1) / (x2 - x1)
        return m

    def get_y_oxy(m, x1, y1):
        b = y1 - m * x1
        return b

    def get_y(m, b, ts):
        Y = m * ts + b
        return Y

    res_x1: Series[int] = na(int)
    res_y1: Series[float] = na(float)
    res_x2: Series[int] = na(int)
    res_y2: Series[float] = na(float)
    sup_x1: Series[int] = na(int)
    sup_y1: Series[float] = na(float)
    sup_x2: Series[int] = na(int)
    sup_y2: Series[float] = na(float)
    res_x1 = phbar2 if cast_bool(ph) else res_x1[1]
    res_y1 = phvalue2 if cast_bool(ph) else res_y1[1]
    res_x2 = phbar3 if cast_bool(ph) else res_x2[1]
    res_y2 = phvalue3 if cast_bool(ph) else res_y2[1]
    res_m = _slope(res_x1, res_x2, res_y1, res_y2)
    res_b = get_y_oxy(res_m, res_x1, res_y1)
    res_y = get_y(res_m, res_b, bar_index)
    sup_x1 = plbar2 if cast_bool(pl) else sup_x1[1]
    sup_y1 = plvalue2 if cast_bool(pl) else sup_y1[1]
    sup_x2 = plbar3 if cast_bool(pl) else sup_x2[1]
    sup_y2 = plvalue3 if cast_bool(pl) else sup_y2[1]
    sup_m = _slope(sup_x1, sup_x2, sup_y1, sup_y2)
    sup_b = get_y_oxy(sup_m, sup_x1, sup_y1)
    sup_y = get_y(sup_m, sup_b, bar_index)
    distance_x = timenow + math.round(ta.change(time) * 1)
    if cast_bool(ph) and phvalue1 > phvalue2 and (buyonly == True):
        line.new(plbar1, plvalue1, phbar1, phvalue1, style=line.style_arrow_right, color=color.lime, width=2)
        line.new(plbar1, phvalue1, phbar1 + rightbars + extend_fibo, phvalue1, style=line.style_solid, color=color.new(color.silver, 60), width=width_fibo)
        line.new(plbar1, phvalue1 - (phvalue1 - plvalue1) * 0.236, phbar1 + rightbars + extend_fibo, phvalue1 - (phvalue1 - plvalue1) * 0.236, style=line.style_solid, color=color.new(color.red, 60), width=width_fibo)
        line.new(plbar1, phvalue1 - (phvalue1 - plvalue1) * 0.382, phbar1 + rightbars + extend_fibo, phvalue1 - (phvalue1 - plvalue1) * 0.382, style=line.style_solid, color=color.new(color.new('#81C784'), 60), width=width_fibo)
        line.new(plbar1, phvalue1 - (phvalue1 - plvalue1) * 0.5, phbar1 + rightbars + extend_fibo, phvalue1 - (phvalue1 - plvalue1) * 0.5, style=line.style_solid, color=color.new(color.green, 60), width=width_fibo)
        line.new(plbar1, phvalue1 - (phvalue1 - plvalue1) * 0.618, phbar1 + rightbars + extend_fibo, phvalue1 - (phvalue1 - plvalue1) * 0.618, style=line.style_solid, color=color.new(color.new('#089981'), 60), width=width_fibo)
        line.new(plbar1, phvalue1 - (phvalue1 - plvalue1) * 0.786, phbar1 + rightbars + extend_fibo, phvalue1 - (phvalue1 - plvalue1) * 0.786, style=line.style_solid, color=color.new(color.aqua, 60), width=width_fibo)
        line.new(plbar1, plvalue1, phbar1 + rightbars + extend_fibo, plvalue1, style=line.style_solid, color=color.new(color.silver, 60), width=width_fibo)
        p1 = line.new(phbar2, phv2low, phbar1 + rightbars + extend_sup_res, phv2low, style=line.style_solid, color=color.new(color.lime, 20), width=width_sup_res)
        p2 = line.new(phbar2, phvalue2, phbar1 + rightbars + extend_sup_res, phvalue2, style=line.style_solid, color=color.new(color.lime, 20), width=width_sup_res)
        linefill.new(p1, p2, color=color.new(color.lime, transp=85))
        if phvalue2 < phvalue3:
            line.new(phbar3, phvalue3, phbar2, phvalue2, style=line.style_dotted, color=color.red, width=width_trendline)
            line.new(phbar2, phvalue2, bar_index, res_y, style=line.style_dotted, color=color.red, width=width_trendline)
        if close < phvalue1 - (phvalue1 - plvalue1) * 0.382 and alert_input == 'Fibo 0.382':
            alert(message='Fibo 0.382', freq=alert.freq_once_per_bar)
        if close < phvalue1 - (phvalue1 - plvalue1) * 0.5 and alert_input == 'Fibo 0.5':
            alert(message='Fibo 0.5', freq=alert.freq_once_per_bar)
        if close < phvalue1 - (phvalue1 - plvalue1) * 0.618 and alert_input == 'Fibo 0.618':
            alert(message='Fibo 0.618', freq=alert.freq_once_per_bar)
        if close < phvalue1 - (phvalue1 - plvalue1) * 0.786 and alert_input == 'Fibo 0.786':
            alert(message='Fibo 0.786', freq=alert.freq_once_per_bar)
        if close < phvalue2 and alert_input == 'Support Zone':
            alert(message='Support Zone', freq=alert.freq_once_per_bar)
        if close < res_y + res_y * 0.005 and alert_input == 'Trendline':
            alert(message='Trendline', freq=alert.freq_once_per_bar)
        labelfibo0: Persistent[Label] = na(Label)
        label.delete(labelfibo0)
        labelfibo0 = label.new(x=distance_x, y=phvalue1 - (phvalue1 - plvalue1) * 0, text='0', color=color.new(color.new('#000000'), 100), textcolor=color_fibo_label, size=size.small, style=label.style_label_left, xloc=xloc.bar_time, yloc=yloc.price)
        labelfibo236: Persistent[Label] = na(Label)
        label.delete(labelfibo236)
        labelfibo236 = label.new(x=distance_x, y=phvalue1 - (phvalue1 - plvalue1) * 0.236, text='0.236', color=color.new(color.new('#000000'), 100), textcolor=color_fibo_label, size=size.small, style=label.style_label_left, xloc=xloc.bar_time, yloc=yloc.price)
        labelfibo382: Persistent[Label] = na(Label)
        label.delete(labelfibo382)
        labelfibo382 = label.new(x=distance_x, y=phvalue1 - (phvalue1 - plvalue1) * 0.382, text='0.382', color=color.new(color.new('#000000'), 100), textcolor=color_fibo_label, size=size.small, style=label.style_label_left, xloc=xloc.bar_time, yloc=yloc.price)
        labelfibo5: Persistent[Label] = na(Label)
        label.delete(labelfibo5)
        labelfibo5 = label.new(x=distance_x, y=phvalue1 - (phvalue1 - plvalue1) * 0.5, text='0.5', color=color.new(color.new('#000000'), 100), textcolor=color_fibo_label, size=size.small, style=label.style_label_left, xloc=xloc.bar_time, yloc=yloc.price)
        labelfibo618: Persistent[Label] = na(Label)
        label.delete(labelfibo618)
        labelfibo618 = label.new(x=distance_x, y=phvalue1 - (phvalue1 - plvalue1) * 0.618, text='0.618', color=color.new(color.new('#000000'), 100), textcolor=color_fibo_label, size=size.small, style=label.style_label_left, xloc=xloc.bar_time, yloc=yloc.price)
        labelfibo786: Persistent[Label] = na(Label)
        label.delete(labelfibo786)
        labelfibo786 = label.new(x=distance_x, y=phvalue1 - (phvalue1 - plvalue1) * 0.786, text='0.786', color=color.new(color.new('#000000'), 100), textcolor=color_fibo_label, size=size.small, style=label.style_label_left, xloc=xloc.bar_time, yloc=yloc.price)
        labelfibo1: Persistent[Label] = na(Label)
        label.delete(labelfibo1)
        labelfibo1 = label.new(x=distance_x, y=phvalue1 - (phvalue1 - plvalue1) * 1, text='1', color=color.new(color.new('#000000'), 100), textcolor=color_fibo_label, size=size.small, style=label.style_label_left, xloc=xloc.bar_time, yloc=yloc.price)
    if cast_bool(pl) and plvalue1 < plvalue2 and (sellonly == True):
        line.new(phbar1, phvalue1, plbar1, plvalue1, style=line.style_arrow_right, color=color.red, width=2)
        line.new(phbar1, plvalue1, plbar1 + rightbars + extend_fibo, plvalue1, style=line.style_solid, color=color.new(color.silver, 60), width=width_fibo)
        line.new(plbar1, plvalue1 - (plvalue1 - phvalue1) * 0.236, plbar1 + rightbars + extend_fibo, plvalue1 - (plvalue1 - phvalue1) * 0.236, style=line.style_solid, color=color.new(color.red, 60), width=width_fibo)
        line.new(plbar1, plvalue1 - (plvalue1 - phvalue1) * 0.382, plbar1 + rightbars + extend_fibo, plvalue1 - (plvalue1 - phvalue1) * 0.382, style=line.style_solid, color=color.new(color.new('#81C784'), 60), width=width_fibo)
        line.new(plbar1, plvalue1 - (plvalue1 - phvalue1) * 0.5, plbar1 + rightbars + extend_fibo, plvalue1 - (plvalue1 - phvalue1) * 0.5, style=line.style_solid, color=color.new(color.green, 60), width=width_fibo)
        line.new(plbar1, plvalue1 - (plvalue1 - phvalue1) * 0.618, plbar1 + rightbars + extend_fibo, plvalue1 - (plvalue1 - phvalue1) * 0.618, style=line.style_solid, color=color.new(color.new('#089981'), 60), width=width_fibo)
        line.new(plbar1, plvalue1 - (plvalue1 - phvalue1) * 0.786, plbar1 + rightbars + extend_fibo, plvalue1 - (plvalue1 - phvalue1) * 0.786, style=line.style_solid, color=color.new(color.aqua, 60), width=width_fibo)
        line.new(phbar1, phvalue1, plbar1 + rightbars + extend_fibo, phvalue1, style=line.style_solid, color=color.new(color.silver, 60), width=width_fibo)
        p1 = line.new(plbar2, plv2low, plbar1 + rightbars + extend_sup_res, plv2low, style=line.style_solid, color=color.new(color.red, 20), width=width_sup_res)
        p2 = line.new(plbar2, plvalue2, plbar1 + rightbars + extend_sup_res, plvalue2, style=line.style_solid, color=color.new(color.red, 20), width=width_sup_res)
        linefill.new(p1, p2, color=color.new(color.red, transp=85))
        if plvalue2 > plvalue3:
            line.new(plbar3, plvalue3, plbar2, plvalue2, style=line.style_dotted, color=color.lime, width=width_trendline)
            line.new(plbar2, plvalue2, bar_index, sup_y, style=line.style_dotted, color=color.lime, width=width_trendline)
        if close > plvalue1 - (plvalue1 - phvalue1) * 0.382 and alertshort_input == 'Fibo 0.382':
            alert(message='Fibo 0.382', freq=alert.freq_once_per_bar)
        if close > plvalue1 - (plvalue1 - phvalue1) * 0.5 and alertshort_input == 'Fibo 0.5':
            alert(message='Fibo 0.5', freq=alert.freq_once_per_bar)
        if close > plvalue1 - (plvalue1 - phvalue1) * 0.618 and alertshort_input == 'Fibo 0.618':
            alert(message='Fibo 0.618', freq=alert.freq_once_per_bar)
        if close > plvalue1 - (plvalue1 - phvalue1) * 0.786 and alertshort_input == 'Fibo 0.786':
            alert(message='Fibo 0.786', freq=alert.freq_once_per_bar)
        if close > plvalue2 and alertshort_input == 'Resistant Zone':
            alert(message='Resistant Zone', freq=alert.freq_once_per_bar)
        if close > sup_y - sup_y * 0.005 and alertshort_input == 'Trendline':
            alert(message='Trendline', freq=alert.freq_once_per_bar)
        labelfibo0: Persistent[Label] = na(Label)
        label.delete(labelfibo0)
        labelfibo0 = label.new(x=distance_x, y=plvalue1 - (plvalue1 - phvalue1) * 0, text='0', color=color.new(color.new('#000000'), 100), textcolor=color_fibo_label, size=size.small, style=label.style_label_left, xloc=xloc.bar_time, yloc=yloc.price)
        labelfibo236: Persistent[Label] = na(Label)
        label.delete(labelfibo236)
        labelfibo236 = label.new(x=distance_x, y=plvalue1 - (plvalue1 - phvalue1) * 0.236, text='0.236', color=color.new(color.new('#000000'), 100), textcolor=color_fibo_label, size=size.small, style=label.style_label_left, xloc=xloc.bar_time, yloc=yloc.price)
        labelfibo382: Persistent[Label] = na(Label)
        label.delete(labelfibo382)
        labelfibo382 = label.new(x=distance_x, y=plvalue1 - (plvalue1 - phvalue1) * 0.382, text='0.382', color=color.new(color.new('#000000'), 100), textcolor=color_fibo_label, size=size.small, style=label.style_label_left, xloc=xloc.bar_time, yloc=yloc.price)
        labelfibo5: Persistent[Label] = na(Label)
        label.delete(labelfibo5)
        labelfibo5 = label.new(x=distance_x, y=plvalue1 - (plvalue1 - phvalue1) * 0.5, text='0.5', color=color.new(color.new('#000000'), 100), textcolor=color_fibo_label, size=size.small, style=label.style_label_left, xloc=xloc.bar_time, yloc=yloc.price)
        labelfibo618: Persistent[Label] = na(Label)
        label.delete(labelfibo618)
        labelfibo618 = label.new(x=distance_x, y=plvalue1 - (plvalue1 - phvalue1) * 0.618, text='0.618', color=color.new(color.new('#000000'), 100), textcolor=color_fibo_label, size=size.small, style=label.style_label_left, xloc=xloc.bar_time, yloc=yloc.price)
        labelfibo786: Persistent[Label] = na(Label)
        label.delete(labelfibo786)
        labelfibo786 = label.new(x=distance_x, y=plvalue1 - (plvalue1 - phvalue1) * 0.786, text='0.786', color=color.new(color.new('#000000'), 100), textcolor=color_fibo_label, size=size.small, style=label.style_label_left, xloc=xloc.bar_time, yloc=yloc.price)
        labelfibo1: Persistent[Label] = na(Label)
        label.delete(labelfibo1)
        labelfibo1 = label.new(x=distance_x, y=plvalue1 - (plvalue1 - phvalue1) * 1, text='1', color=color.new(color.new('#000000'), 100), textcolor=color_fibo_label, size=size.small, style=label.style_label_left, xloc=xloc.bar_time, yloc=yloc.price)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
