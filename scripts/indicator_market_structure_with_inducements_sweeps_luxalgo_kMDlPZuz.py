"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_method import method_call
from pynecore.lib import (
    bar_index, barstate, close, color, fixnan, high, input, label, line, low,
    math, na, plot, script, size, ta
)
from pynecore.types import Color, NA, Persistent, PersistentSeries, Series


@script.indicator('Market Structure with Inducements & Sweeps [LuxAlgo]', 'LuxAlgo - Market Structure with Inducements & Sweeps', overlay=True, max_lines_count=500, max_labels_count=500)
def main(
    len=input(50, 'CHoCH Detection Period'),
    shortLen=input(3, 'IDM Detection Period'),
    bullCss=input(color.new('#089981'), 'Bullish Elements', group='Style'),
    bearCss=input(color.new('#FF5252'), 'Bearish Elements', group='Style'),
    showChoch=input(True, 'Show CHoCH', group='Style'),
    showBos=input(True, 'Show BOS', group='Style'),
    showIdm=input(True, 'Show Inducements', inline='idm', group='Style'),
    idmCss=input(color.gray, '', inline='idm', group='Style'),
    showSweeps=input(True, 'Show Sweeps', inline='sweeps', group='Style'),
    sweepsCss=input(color.gray, '', inline='sweeps', group='Style'),
    showCircles=input(True, 'Show Swings', group='Style')
):
    n: Series = bar_index
    def swings(len):
        __hist_n__: Series = n[0]
        os: PersistentSeries[int] = 0
        topx: Persistent[int] = na(int)
        btmx: Persistent[int] = na(int)
        upper = ta.highest(len)
        lower = ta.lowest(len)
        os = 0 if high[len] > upper else 1 if low[len] < lower else os[1]
        top = high[len] if os == 0 and os[1] != 0 else na
        topx = __hist_n__[len] if os == 0 and os[1] != 0 else topx
        btm = low[len] if os == 1 and os[1] != 1 else na
        btmx = __hist_n__[len] if os == 1 and os[1] != 1 else btmx
        return (top, topx, btm, btmx)

    top, topx, btm, btmx = swings(len)
    stop, stopx, sbtm, sbtmx = swings(shortLen)
    os: PersistentSeries[int] = 0
    top_crossed: Persistent[bool] = False
    btm_crossed: Persistent[bool] = False
    max: PersistentSeries[float] = na(float)
    min: PersistentSeries[float] = na(float)
    max_x1: Persistent[int] = na(int)
    min_x1: Persistent[int] = na(int)
    topy: Persistent[float] = na(float)
    btmy: Persistent[float] = na(float)
    stop_crossed: Persistent[bool] = False
    sbtm_crossed: Persistent[bool] = False
    if top:
        topy = top
        top_crossed = False
    if btm:
        btmy = btm
        btm_crossed = False
    if close > topy and (not top_crossed):
        os = 1
        top_crossed = True
    if close < btmy and (not btm_crossed):
        os = 0
        btm_crossed = True
    if os != os[1]:
        max = high
        min = low
        max_x1 = n
        min_x1 = n
        stop_crossed = False
        sbtm_crossed = False
        if os == 1 and showChoch:
            line.new(topx, topy, n, topy, color=bullCss, style=line.style_dashed)
            label.new(cast_int(math.avg(n, topx)), topy, 'CHoCH', color=NA(Color), style=label.style_label_down, textcolor=bullCss, size=size.tiny)
        elif showChoch:
            line.new(btmx, btmy, n, btmy, color=bearCss, style=line.style_dashed)
            label.new(cast_int(math.avg(n, btmx)), btmy, 'CHoCH', color=NA(Color), style=label.style_label_up, textcolor=bearCss, size=size.tiny)
    stopy = fixnan(stop)
    sbtmy = fixnan(sbtm)
    if low < sbtmy and (not sbtm_crossed) and (os == 1) and (sbtmy != btmy):
        if showIdm:
            line.new(sbtmx, sbtmy, n, sbtmy, color=idmCss, style=line.style_dotted)
            label.new(cast_int(math.avg(n, sbtmx)), sbtmy, 'IDM', color=NA(Color), style=label.style_label_up, textcolor=idmCss, size=size.tiny)
        sbtm_crossed = True
    if close > max and sbtm_crossed and (os == 1):
        if showBos:
            line.new(max_x1, max, n, max, color=bullCss)
            label.new(cast_int(math.avg(n, max_x1)), max, 'BOS', color=NA(Color), style=label.style_label_down, textcolor=bullCss, size=size.tiny)
        sbtm_crossed = False
    if high > stopy and (not stop_crossed) and (os == 0) and (stopy != topy):
        if showIdm:
            line.new(stopx, stopy, n, stopy, color=color.gray, style=line.style_dotted)
            label.new(cast_int(math.avg(n, stopx)), stopy, 'IDM', color=NA(Color), style=label.style_label_down, textcolor=color.gray, size=size.tiny)
        stop_crossed = True
    if close < min and stop_crossed and (os == 0):
        if showBos:
            line.new(min_x1, min, n, min, color=bearCss)
            label.new(cast_int(math.avg(n, min_x1)), min, 'BOS', color=NA(Color), style=label.style_label_up, textcolor=bearCss, size=size.tiny)
        stop_crossed = False
    if high > max and close < max and (os == 1) and (n - max_x1 > 1) and showSweeps:
        line.new(max_x1, max, n, max, color=sweepsCss, style=line.style_dotted)
        label.new(cast_int(math.avg(n, max_x1)), max, 'x', color=NA(Color), style=label.style_label_down, textcolor=sweepsCss)
    if low < min and close > min and (os == 0) and (n - min_x1 > 1) and showSweeps:
        line.new(min_x1, min, n, min, color=sweepsCss, style=line.style_dotted)
        label.new(cast_int(math.avg(n, min_x1)), min, 'x', color=NA(Color), style=label.style_label_up, textcolor=sweepsCss)
    max = math.max(high, max)
    min = math.min(low, min)
    if max > max[1]:
        max_x1 = n
    if min < min[1]:
        min_x1 = n
    ext_choch: Persistent = line.new(na, na, na, na, style=line.style_dashed)
    ext_bos: Persistent = line.new(na, na, na, na)
    ext_idm: Persistent = line.new(na, na, na, na, style=line.style_dotted, color=idmCss)
    ext_choch_lbl: Persistent = label.new(na, na, 'CHoCH', color=NA(Color), size=size.tiny)
    ext_bos_lbl: Persistent = label.new(na, na, 'BOS', color=NA(Color), size=size.tiny)
    ext_idm_lbl: Persistent = label.new(na, na, 'IDM', color=NA(Color), size=size.tiny, textcolor=idmCss)
    if barstate.islast:
        if os == 1:
            if showChoch:
                method_call('set_xy1', ext_choch, btmx, btmy)
                method_call('set_xy2', ext_choch, n, btmy)
                method_call('set_color', ext_choch, bearCss)
                method_call('set_xy', ext_choch_lbl, n, btmy)
                method_call('set_style', ext_choch_lbl, label.style_label_up)
                method_call('set_textcolor', ext_choch_lbl, bearCss)
            if showBos:
                method_call('set_xy1', ext_bos, max_x1, max)
                method_call('set_xy2', ext_bos, n, max)
                method_call('set_color', ext_bos, bullCss)
                method_call('set_xy', ext_bos_lbl, n, max)
                method_call('set_style', ext_bos_lbl, label.style_label_down)
                method_call('set_textcolor', ext_bos_lbl, bullCss)
            if not sbtm_crossed and showIdm:
                method_call('set_xy1', ext_idm, sbtmx, sbtmy)
                method_call('set_xy2', ext_idm, n + 15, sbtmy)
                method_call('set_xy', ext_idm_lbl, n + 15, sbtmy)
                method_call('set_style', ext_idm_lbl, label.style_label_up)
                method_call('set_color', ext_idm, idmCss)
                method_call('set_textcolor', ext_idm_lbl, idmCss)
            else:
                method_call('set_color', ext_idm, na)
                method_call('set_textcolor', ext_idm_lbl, na)
        else:
            if showChoch:
                method_call('set_xy1', ext_choch, topx, topy)
                method_call('set_xy2', ext_choch, n, topy)
                method_call('set_color', ext_choch, bullCss)
                method_call('set_xy', ext_choch_lbl, n, topy)
                method_call('set_style', ext_choch_lbl, label.style_label_down)
                method_call('set_textcolor', ext_choch_lbl, bullCss)
            if showBos:
                method_call('set_xy1', ext_bos, min_x1, min)
                method_call('set_xy2', ext_bos, n, min)
                method_call('set_color', ext_bos, bearCss)
                method_call('set_xy', ext_bos_lbl, n, min)
                method_call('set_style', ext_bos_lbl, label.style_label_up)
                method_call('set_textcolor', ext_bos_lbl, bearCss)
            if not stop_crossed and showIdm:
                method_call('set_xy1', ext_idm, stopx, stopy)
                method_call('set_xy2', ext_idm, n + 15, stopy)
                method_call('set_xy', ext_idm_lbl, n + 15, stopy)
                method_call('set_style', ext_idm_lbl, label.style_label_down)
                method_call('set_color', ext_idm, idmCss)
                method_call('set_textcolor', ext_idm_lbl, idmCss)
            else:
                method_call('set_color', ext_idm, na)
                method_call('set_textcolor', ext_idm_lbl, na)
    plot(top if showCircles else na, 'Swing High', color.new(bearCss, 50), 5, plot.style_circles, offset=-len)
    plot(btm if showCircles else na, 'Swing Low', color.new(bullCss, 50), 5, plot.style_circles, offset=-len)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
