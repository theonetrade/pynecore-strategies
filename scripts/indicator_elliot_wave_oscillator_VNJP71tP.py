"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, input, plot, script, ta
from pynecore.types import Series


@script.indicator(title='Elliott Wave Oscillator', shorttitle='EWO')
def main(
    src: Series[float] = input(close, title='source'),
    sma1length=input(5),
    sma2length=input(35),
    UsePercent=input.bool(True, 'Show Dif as percent of current Candle')
):
    smadif = (ta.sma(src, sma1length) - ta.sma(src, sma2length)) / src * 100 if UsePercent else ta.sma(src, sma1length) - ta.sma(src, sma2length)
    col = color.red if smadif <= 0 else color.green
    plot(smadif, color=col, linewidth=2, style=plot.style_histogram)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
