"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_loop
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    alertcondition, bar_index, barcolor, close, color, fill, high, hline,
    input, line, low, na, nz, plot, script, ta
)
from pynecore.types import PersistentSeries, Series


@script.indicator('RSI Tops and Bottoms', max_bars_back=300, na_bool=True)
def main(
    len=input.int(14, minval=1, title='RSI Length'),
    src: Series[float] = input(close, 'RSI Source'),
    ob=input(defval=70, title='Upper Band'),
    os=input(defval=30, title='lower Band'),
    prd=input(defval=10, title='Max Number of Bars in OB/OS'),
    mindis=input(defval=5, title='Min Number of Bars between Tops/Bottoms'),
    maxdis=input(defval=100, title='Max Number of Bars between Topss/Bottoms'),
    topcol=input.color(defval=color.red, title='Line Colors', inline='cols'),
    bottomcol=input.color(defval=color.lime, title='', inline='cols'),
    lwidth=input.int(defval=2, title='Line Width', minval=1, maxval=4),
    chbarcol=input(defval=True, title='Change Bar Color')
):
    rsi: Series = ta.rsi(src, len)
    plot(rsi, 'RSI', color=color.new(color.new('#8E1599'), 0))
    band1 = hline(ob, 'Upper Band', color=color.new('#C0C0C0'))
    band0 = hline(os, 'Lower Band', color=color.new('#C0C0C0'))
    fill(band1, band0, color=color.new(color.new('#9915FF'), 90), title='Background')
    belowos: PersistentSeries[bool] = False
    oscount: PersistentSeries[int] = 0
    belowos = True if rsi[1] >= os and rsi < os else False if rsi > os else belowos
    oscount = oscount + 1 if belowos else 0 if not belowos else oscount
    lastlowestrsi: PersistentSeries[float] = na(float)
    lastlowestprice: PersistentSeries[float] = na(float)
    lastlowestbi: PersistentSeries[int] = na(int)
    itsfineos: PersistentSeries[bool] = False
    maygoup: bool = False
    if belowos[1] and (not belowos) and (nz(oscount[1]) > 0):
        lastlowestrsi = 101
        lastlowestbi = bar_index
        itsfineos = True
        __loop_1__ = pine_loop(1, 1)
        while __loop_1__.step(oscount[1]):
            x = __loop_1__.value
            if x > prd:
                itsfineos = False
            if rsi[x] < lastlowestrsi:
                lastlowestrsi = rsi[x]
                lastlowestbi = bar_index - x
                lastlowestprice = low[x]
    if ta.change(lastlowestrsi) != 0 and cast_bool(lastlowestrsi) and cast_bool(lastlowestrsi[1]) and (lastlowestrsi > lastlowestrsi[1]) and (lastlowestprice < lastlowestprice[1]) and (bar_index - lastlowestbi[1] < maxdis) and itsfineos and itsfineos[1] and (bar_index - lastlowestbi[1] > mindis):
        line.new(x1=bar_index, y1=lastlowestrsi, x2=lastlowestbi[1], y2=lastlowestrsi[1], color=bottomcol, width=lwidth, style=line.style_arrow_left)
        maygoup = True
    aboveob: PersistentSeries[bool] = False
    obcount: PersistentSeries[int] = 0
    aboveob = True if rsi[1] <= ob and rsi > ob else False if rsi < ob else aboveob
    obcount = obcount + 1 if aboveob else 0 if not aboveob else obcount
    lasthighestrsi: PersistentSeries[float] = na(float)
    lasthighestprice: PersistentSeries[float] = na(float)
    lasthighestbi: PersistentSeries[int] = na(int)
    itsfineob: PersistentSeries[bool] = False
    maygodown: bool = False
    if aboveob[1] and (not aboveob) and (nz(obcount[1]) > 0):
        lasthighestrsi = -1
        lasthighestbi = bar_index
        itsfineob = True
        __loop_1__ = pine_loop(1, 1)
        while __loop_1__.step(obcount[1]):
            x = __loop_1__.value
            if x > prd:
                itsfineob = False
            if rsi[x] > lasthighestrsi:
                lasthighestrsi = rsi[x]
                lasthighestbi = bar_index - x
                lasthighestprice = high[x]
    if ta.change(lasthighestrsi) != 0 and cast_bool(lasthighestrsi) and cast_bool(lasthighestrsi[1]) and (lasthighestrsi < lasthighestrsi[1]) and (lasthighestprice > lasthighestprice[1]) and (bar_index - lasthighestbi[1] < maxdis) and itsfineob and itsfineob[1] and (bar_index - lasthighestbi[1] > mindis):
        line.new(x1=bar_index, y1=lasthighestrsi, x2=lasthighestbi[1], y2=lasthighestrsi[1], color=topcol, width=lwidth, style=line.style_arrow_left)
        maygodown = True
    iff_1 = color.black if maygodown else na
    iff_2 = color.blue if maygoup else iff_1
    barcolor(color=iff_2 if chbarcol else na)
    alertcondition(maygoup, title='Divergence at Bottoms', message='Divergence at Bottom, Price may go UP')
    alertcondition(maygodown, title='Divergence at Tops', message='Divergence at Bottom, Price may go DOWN')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
