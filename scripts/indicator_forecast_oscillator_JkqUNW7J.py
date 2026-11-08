"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, hline, input, plot, script, ta
from pynecore.types import Series


@script.indicator('Forecast Oscillator', overlay=False, na_bool=True)
def main(
    src: Series[float] = input(close),
    len=input.int(defval=14, minval=1, title='Length')
):
    lrc = ta.linreg(src, len, 0)
    lrc1 = ta.linreg(src, len, 1)
    lrs = lrc - lrc1
    TSF: Series = ta.linreg(src, len, 0) + lrs
    fosc: Series = 100 * (src - TSF[1]) / src
    col12 = fosc > fosc[1]
    col32 = fosc < fosc[1]
    color2 = color.new('#21C400') if col12 else color.new('#960012') if col32 else color.blue
    plot(fosc, color=color2, linewidth=2, title='TSF')
    hline(0, linestyle=hline.style_dashed, color=color.blue)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
