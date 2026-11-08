"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, hline, input, plot, script, ta
from pynecore.types import Series


@script.indicator(title='RCI3lines', shorttitle='RCI3lines')
def main(
    itvs=input(9, 'short interval'),
    itvm=input(36, 'middle interval'),
    itvl=input(52, 'long interval'),
    src: Series[float] = input(close, 'source'),
    upperband=input(title='High line[%]', defval=80),
    lowerband=input(title='Low line[%]', defval=-80)
):
    hline(upperband, color=color.gray, linestyle=hline.style_dashed)
    hline(lowerband, color=color.gray, linestyle=hline.style_dashed)

    plot(ta.rci(src, itvs), title='RCI short', color=color.new(color.red, 0))
    plot(ta.rci(src, itvm), title='RCI middle', color=color.new(color.blue, 0))
    plot(ta.rci(src, itvl), title='RCI long', color=color.new(color.green, 0))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
