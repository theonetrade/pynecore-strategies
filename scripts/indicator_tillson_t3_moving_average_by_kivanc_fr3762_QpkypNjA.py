"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import alertcondition, close, color, high, input, low, na, plot, script, ta
from pynecore.types import Series


@script.indicator('Tillson T3', overlay=True, na_bool=True)
def main(
    T3FiboLine=input(False, title='Show T3 Fibonacci Ratio Line?'),
    length1=input(8, 'T3 Length'),
    a1=input(0.7, 'Volume Factor'),
    length12=input(5, 'T3 Length fibo'),
    a12=input(0.618, 'Volume Factor fibo')
):
    e1 = ta.ema((high + low + 2 * close) / 4, length1)
    e2 = ta.ema(e1, length1)
    e3 = ta.ema(e2, length1)
    e4 = ta.ema(e3, length1)
    e5 = ta.ema(e4, length1)
    e6 = ta.ema(e5, length1)
    c1 = -a1 * a1 * a1
    c2 = 3 * a1 * a1 + 3 * a1 * a1 * a1
    c3 = -6 * a1 * a1 - 3 * a1 - 3 * a1 * a1 * a1
    c4 = 1 + 3 * a1 + a1 * a1 * a1 + 3 * a1 * a1
    T3: Series = c1 * e6 + c2 * e5 + c3 * e4 + c4 * e3
    col1 = T3 > T3[1]
    col3 = T3 < T3[1]
    color_1 = color.green if col1 else color.red if col3 else color.yellow
    plot(T3, color=color_1, linewidth=3, title='T3')
    e12 = ta.ema((high + low + 2 * close) / 4, length12)
    e22 = ta.ema(e12, length12)
    e32 = ta.ema(e22, length12)
    e42 = ta.ema(e32, length12)
    e52 = ta.ema(e42, length12)
    e62 = ta.ema(e52, length12)
    c12 = -a12 * a12 * a12
    c22 = 3 * a12 * a12 + 3 * a12 * a12 * a12
    c32 = -6 * a12 * a12 - 3 * a12 - 3 * a12 * a12 * a12
    c42 = 1 + 3 * a12 + a12 * a12 * a12 + 3 * a12 * a12
    T32: Series = c12 * e62 + c22 * e52 + c32 * e42 + c42 * e32
    col12 = T32 > T32[1]
    col32 = T32 < T32[1]
    color2 = color.blue if col12 else color.purple if col32 else color.yellow
    plot(T32 if T3FiboLine and cast_bool(T32) else na, color=color2, linewidth=2, title='T3fibo')
    alertcondition(ta.crossover(T3, T3[1]), title='T3 BUY', message='T3 BUY!')
    alertcondition(ta.crossunder(T3, T3[1]), title='T3 SELL', message='T3 SELL!')
    alertcondition(ta.cross(T3, T3[1]), title='Color ALARM', message='T3 has changed color!')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
