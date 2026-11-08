"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, bar_index, bgcolor, close, color, fill, hline, input,
    label, math, na, plot, script, size, ta, yloc
)
from pynecore.types import NA, Series


@script.indicator(title='Relative Strength Index - Divergences - Libertus', shorttitle='RSI Div - Lib', na_bool=True)
def main(
    len=input.int(14, minval=1, title='RSI Length'),
    ob=input.int(defval=70, title='Overbought', minval=0, maxval=100),
    os=input.int(defval=30, title='Oversold', minval=0, maxval=100),
    omid=input.int(defval=50, title='Midline value', minval=0, maxval=100),
    omidh=input(defval=False, title='Hide midline'),
    piv=input(False, 'Hide pivots?'),
    shrt=input(False, 'Shorter labels?'),
    hidel=input(False, 'Hide labels and color background'),
    xbars=input.int(defval=90, title='Div lookback period (bars)?', minval=1)
):
    rsi: Series = ta.rsi(close, len)
    band1 = hline(ob)
    band0 = hline(os)
    band3 = hline(omid, color=color.new(color.black, 100 if omidh else 80))
    plot(rsi, color=color.new(color.red, 0) if rsi > ob or rsi < os else color.new(color.black, 0))
    fill(band3, band1, color=color.new(color.lime, 96))
    fill(band0, band3, color=color.new(color.red, 96))
    hb = math.abs(ta.highestbars(rsi, xbars))
    lb = math.abs(ta.lowestbars(rsi, xbars))
    max: Series = NA(float)
    max_rsi: Series = NA(float)
    min: Series = NA(float)
    min_rsi: Series = NA(float)
    pivoth = NA(bool)
    pivotl = NA(bool)
    divbear = NA(bool)
    divbull = NA(bool)
    max = close if hb == 0 else close if na(max[1]) else max[1]
    max_rsi = rsi if hb == 0 else rsi if na(max_rsi[1]) else max_rsi[1]
    min = close if lb == 0 else close if na(min[1]) else min[1]
    min_rsi = rsi if lb == 0 else rsi if na(min_rsi[1]) else min_rsi[1]
    if close > max:
        max = close
    if rsi > max_rsi:
        max_rsi = rsi
    if close < min:
        min = close
    if rsi < min_rsi:
        min_rsi = rsi
    pivoth = True if max_rsi == max_rsi[2] and max_rsi[2] != max_rsi[3] else False
    pivotl = True if min_rsi == min_rsi[2] and min_rsi[2] != min_rsi[3] else False
    if max[1] > max[2] and rsi[1] < max_rsi and (rsi <= rsi[1]):
        divbear = True
    if min[1] < min[2] and rsi[1] > min_rsi and (rsi >= rsi[1]):
        divbull = True
    alertcondition(divbear, title='Bear div', message='Bear div')
    alertcondition(divbull, title='Bull div', message='Bull div')
    alertcondition(pivoth, title='Pivot high', message='Pivot high')
    alertcondition(pivotl, title='Pivot low', message='Pivot low')
    l = label.new(bar_index - 1, rsi[1] + 1, 'BEAR', color=color.red, textcolor=color.white, style=label.style_label_down, yloc=yloc.price, size=size.small) if divbear else label.new(bar_index - 1, rsi[1] - 1, 'BULL', color=color.green, textcolor=color.white, style=label.style_label_up, yloc=yloc.price, size=size.small) if divbull else label.new(bar_index - 2, max_rsi + 1, 'PIVOT', color=color.blue, textcolor=color.white, style=label.style_label_down, yloc=yloc.price, size=size.small) if pivoth else label.new(bar_index - 2, min_rsi - 1, 'PIVOT', color=color.blue, textcolor=color.white, style=label.style_label_up, yloc=yloc.price, size=size.small) if pivotl else na
    if shrt:
        label.set_text(l, na)
    if piv and (pivoth or pivotl) or hidel:
        label.delete(l)
    bgcolor((color.new(color.red, 50) if divbear else color.new(color.green, 50) if divbull else na) if hidel else na, offset=-1)
    bgcolor((na if piv else color.new(color.blue, 50) if pivoth or pivotl else na) if hidel else na, offset=-2)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
