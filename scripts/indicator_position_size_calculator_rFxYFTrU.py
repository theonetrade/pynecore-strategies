"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    color, fill, input, label, math, na, ohlc4, plot, script, size, string,
    syminfo, time, xloc, yloc
)
from pynecore.types import Label, NA, Persistent


@script.indicator('Position Size Calculator', 'Calc', True, na_bool=True)
def main(
    accbalance=input(1000.0, title='Account Balance'),
    riskper=input(2.0, title='Risk Percentage'),
    entry=input(0.0, title='Entry'),
    sl=input(0.0, title='Stop Loss'),
    tp=input(0.0, title='Target Price'),
    showscr=input(True, 'Show Position Size Label'),
    posscrX=input(30, 'Position Size Label x-axis'),
    col=input(color.white, title='Text Color'),
    showLabel=input(True, title='Show R/R box labels'),
    poslblX=input(10, 'R/R Label x-axis')
):
    sldist = entry - sl
    tgdist = tp - entry
    slper = sldist / entry * 100
    tgper = tgdist / entry * 100
    rr = tgper / slper
    size__ren__ = accbalance * riskper / slper
    entryp = plot(entry, show_last=20, offset=20, title='Entry', color=color.new('#787B8600'))
    tpp = plot(tp, show_last=20, offset=20, title='TP', color=color.new('#4CAF5000'))
    slp = plot(sl, show_last=20, offset=20, title='SL', color=color.new('#FF525200'))
    fill(entryp, tpp, show_last=1, color=color.new(color.green, 50))
    fill(entryp, slp, show_last=1, color=color.new(color.red, 50))
    def f_tickFormat():
        _s = string.tostring(syminfo.mintick)
        _s = string.replace_all(_s, '25', '00')
        _s = string.replace_all(_s, '5', '0')
        _s = string.replace_all(_s, '1', '0')
        return _s

    def f_color(_val):
        return color.new('#00000000') if _val else na

    def f_print(_txt):
        _lbl: Persistent = NA(Label)
        label.delete(_lbl)
        _lbl = label.new(time + (time - time[1]) * posscrX, ohlc4[1], _txt, xloc.bar_time, yloc.price, f_color(showscr), textcolor=col if showscr else na, size=size.normal, style=label.style_label_center)
        return _lbl

    f_print('\n Account Balance : ' + string.tostring(accbalance) + '\n Risk % : ' + string.tostring(riskper) + '\n\n Entry: ' + string.tostring(entry) + '\n Target : ' + string.tostring(tp) + '\n Stop Loss : ' + string.tostring(sl) + '\n\n Position Size : ' + string.tostring(math.abs(size__ren__), f_tickFormat()) + '\n R/R : ' + string.tostring(rr, '#.##') + ' R')
    def f_colorl(_val):
        return color.new('#4CAF50') if _val else na

    def f_printl(_txt):
        _lbl: Persistent = NA(Label)
        label.delete(_lbl)
        _lbl = label.new(time + (time - time[1]) * poslblX, tp, _txt, xloc.bar_time, yloc.price, f_colorl(showLabel), textcolor=color.white if showLabel else na, size=size.normal, style=label.style_label_center)
        return _lbl

    f_printl('Target: ' + string.tostring(tgdist) + ' (' + string.tostring(tgper, '#.##') + '%)')
    def f_colors(_val):
        return color.new('#FF5252') if _val else na

    def f_prints(_txt):
        _lbl: Persistent = NA(Label)
        label.delete(_lbl)
        _lbl = label.new(time + (time - time[1]) * poslblX, sl, _txt, xloc.bar_time, yloc.price, f_colors(showLabel), textcolor=color.white if showLabel else na, size=size.normal, style=label.style_label_center)
        return _lbl

    f_prints('Stop: ' + string.tostring(sldist) + ' (' + string.tostring(slper, '#.##') + '%)')
    def f_colore(_val):
        return color.new('#787B86') if _val else na

    rrlbl = '\n Account Balance : ' + string.tostring(accbalance) + '\n Risk % : ' + string.tostring(riskper) + '\n\n Position Size : ' + string.tostring(math.abs(size__ren__), f_tickFormat())
    def f_printe(_txt):
        _lbl: Persistent = NA(Label)
        label.delete(_lbl)
        _lbl = label.new(time + (time - time[1]) * poslblX, entry, _txt, xloc.bar_time, yloc.price, f_colore(showLabel), textcolor=color.white if showLabel else na, size=size.normal, style=label.style_label_center, tooltip=rrlbl)
        return _lbl

    f_printe('R/R: ' + string.tostring(rr, '#.##'))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
