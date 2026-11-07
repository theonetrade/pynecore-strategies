"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    alertcondition, array, bgcolor, close, color, display, fill, hline,
    input, last_bar_index, line, low, math, na, plot, scale, script, strategy, ta
)
from pynecore.types import Line, Series


@script.strategy('RSI Divergence Strategy', overlay=True, scale=scale.none, margin_long=0, margin_short=0, initial_capital=1000000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True)
def main(
    rsilen=input.int(14, title='rsi length'),
    rsisrc: Series[float] = input(close, title='source'),
    len=input.int(14, title='RSI Divergence length', maxval=500),
    tpb=input.float(25, title='take profit', group='buy', step=0.5),
    sb=input.float(5, title='stop', group='buy', step=0.5),
    tsb=input.float(0.25, title='trailing stop', group='buy', step=0.5),
    tps=input.float(25, title='take profit', group='sell', step=0.5),
    ss=input.float(5, title='stop', group='sell', step=0.5),
    tss=input.float(0.25, title='trailing stop', group='sell', step=0.5),
    zoom=input.int(0, title='zoom', maxval=27, minval=-27)
):
    x: Series = ta.rsi(rsisrc, rsilen)
    src: Series = close
    extrapolation: int = 0
    hline(300 - zoom * 10, color=color.rgb(54, 58, 69, 100))
    hline(10, color=color.rgb(54, 58, 69, 100))
    xo: float = 0.0
    yo: float = 0.0
    xyo: float = 0.0
    xxo: float = 0.0
    for i in pine_range(0, len - 1, 1):
        xo = xo + i / len
        yo = yo + x[len - 1 - i] / len
        xyo = xyo + i * x[len - 1 - i] / len
        xxo = xxo + i * i / len
    dnm = ta.lowest(low, 200)
    dizi: list[float] = array.new_float(len * 2 + 1 + extrapolation)
    linedizi: list[Line] = array.new_line()
    a = (xo * yo - xyo) / (xo * xo - xxo)
    b = yo - a * xo
    for i in pine_range(0, len - 1 + extrapolation, 1):
        array.set(dizi, i, a * i + b)
    xo2: float = 0.0
    yo2: float = 0.0
    xyo2: float = 0.0
    xxo2: float = 0.0
    for i in pine_range(0, len - 1, 1):
        xo2 = xo2 + i / len
        yo2 = yo2 + src[len - 1 - i] / len
        xyo2 = xyo2 + i * src[len - 1 - i] / len
        xxo2 = xxo2 + i * i / len
    dizi2: list[float] = array.new_float(len * 2 + 1 + extrapolation)
    linedizi2: list[Line] = array.new_line()
    a2 = (xo2 * yo2 - xyo2) / (xo2 * xo2 - xxo2)
    b2 = yo2 - a * xo2
    for i in pine_range(0, len - 1 + extrapolation, 1):
        array.set(dizi2, i, a2 * i + b2)
    ttk: Series = 1 if array.get(dizi, 0) < array.get(dizi, 1) and array.get(dizi2, 0) > array.get(dizi2, 1) else -1 if array.get(dizi, 0) > array.get(dizi, 1) and array.get(dizi2, 0) < array.get(dizi2, 1) else 0
    cg = array.get(dizi, 0) < array.get(dizi, 1) and array.get(dizi2, 0) > array.get(dizi2, 1)
    cr = array.get(dizi, 0) > array.get(dizi, 1) and array.get(dizi2, 0) < array.get(dizi2, 1)
    highest_1 = ta.highest(ttk[1], len / 2)
    bgcolor(color=color.rgb(76, 175, 79, 50) if cg and highest_1 < 1 else color.rgb(255, 82, 82, 50) if cr and ta.lowest(ttk[1], len / 2) > -1 else na, offset=0, display=display.none)
    plot(x)
    xo3: float = 0.0
    yo3: float = 0.0
    xyo3: float = 0.0
    xxo3: float = 0.0
    for i in pine_range(0, len - 1, 1):
        xo3 = xo3 + i / len
        yo3 = yo3 + x[len - 1 - i + ta.barssince(cg)] / len
        xyo3 = xyo3 + i * x[len - 1 - i + ta.barssince(cg)] / len
        xxo3 = xxo3 + i * i / len
    dizi3: list[float] = array.new_float(len * 2 + 1 + extrapolation)
    linedizi3: list[Line] = array.new_line()
    a3 = (xo3 * yo3 - xyo3) / (xo3 * xo3 - xxo3)
    b3 = yo3 - a3 * xo3
    for i in pine_range(0, len - 1 + extrapolation, 1):
        array.set(dizi3, i, a3 * i + b3)
    xo4: float = 0.0
    yo4: float = 0.0
    xyo4: float = 0.0
    xxo4: float = 0.0
    for i in pine_range(0, len - 1, 1):
        xo4 = xo4 + i / len
        yo4 = yo4 + x[len - 1 - i + ta.barssince(cr)] / len
        xyo4 = xyo4 + i * x[len - 1 - i + ta.barssince(cr)] / len
        xxo4 = xxo4 + i * i / len
    dizi4: list[float] = array.new_float(len * 2 + 1 + extrapolation)
    linedizi4: list[Line] = array.new_line()
    a4 = (xo4 * yo4 - xyo4) / (xo4 * xo4 - xxo4)
    b4 = yo4 - a4 * xo4
    for i in pine_range(0, len - 1 + extrapolation, 1):
        array.set(dizi4, i, a4 * i + b4)
    line__ren__: Series = line.new(last_bar_index - ta.barssince(cg) - len, array.get(dizi3, 0), last_bar_index - ta.barssince(cg), array.get(dizi3, len - 1), color=color.rgb(0, 255, 0), width=2)
    line2: Series = line.new(last_bar_index - ta.barssince(cr) - len, array.get(dizi4, 0), last_bar_index - ta.barssince(cr), array.get(dizi4, len - 1), color=color.rgb(255, 0, 0, 0), width=2)
    line.delete(line__ren__[1])
    line.delete(line2[1])
    highest_2 = ta.highest(ttk[1], len / 2)
    lowest_1 = ta.lowest(ttk[1], len / 2)
    alert__ren__ = array.get(dizi, 0) < array.get(dizi, 1) and array.get(dizi2, 0) > array.get(dizi2, 1) and (highest_2 < 1) or (array.get(dizi, 0) > array.get(dizi, 1) and array.get(dizi2, 0) < array.get(dizi2, 1) and (lowest_1 > -1))
    alertcondition(alert__ren__)
    hline(50)
    rs = hline(30)
    rss = hline(70)
    fill(rs, rss, color=color.rgb(126, 87, 194, 90), title='RSI Background Fill')
    highest_3 = ta.highest(ttk[1], len / 2)
    longCondition = cg and highest_3 < 1
    if longCondition:
        strategy.entry('Long', strategy.long, qty=math.round(x))
        strategy.exit('exit long', 'Long', limit=close * (100 + tpb) / 100, stop=close * (100 - sb) / 100, trail_price=close, trail_offset=close * tsb)
    lowest_2 = ta.lowest(ttk[1], len / 2)
    shortCondition = cr and lowest_2 > -1
    if shortCondition:
        strategy.entry('Short', strategy.short, qty=math.round(100 - x))
        strategy.exit('exit short', 'Short', limit=close * (100 - tps) / 100, stop=close * (100 + ss) / 100, trail_price=close, trail_offset=close * tss)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
