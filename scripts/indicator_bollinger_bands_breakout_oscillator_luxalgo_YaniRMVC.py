"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import close, color, fill, hline, input, math, na, plot, script, ta
from pynecore.types import Series


@script.indicator('Bollinger Bands Breakout Oscillator [LUX]', 'BBands BO [LuxAlgo]')
def main(
    length=input(14),
    mult=input(1.0),
    src: Series[float] = input(close),
    bull_css=input(color.new('#089981'), 'Bullish Color', group='Style'),
    bear_css=input(color.new('#F23645'), 'Bearish Color', group='Style')
):
    stdev = ta.stdev(src, length) * mult
    ema = ta.ema(src, length)
    upper: Series = ema + stdev
    lower: Series = ema - stdev
    bull: float = 0.0
    bear: float = 0.0
    bull_den: float = 0.0
    bear_den: float = 0.0
    for i in pine_range(0, length - 1, 1):
        bull = bull + math.max(src[i] - upper[i], 0)
        bear = bear + math.max(lower[i] - src[i], 0)
        bull_den = bull_den + math.abs(src[i] - upper[i])
        bear_den = bear_den + math.abs(lower[i] - src[i])
    bull = bull / bull_den * 100
    bear = bear / bear_den * 100
    bull_grad = color.from_gradient(bull, 0, 100, color.new(bull_css, 100), color.new(bull_css, 50))
    bear_grad = color.from_gradient(bear, 0, 100, color.new(bear_css, 100), color.new(bear_css, 50))
    plot0 = plot(bull, color=na if bull == 0 else bull_css)
    plot1 = plot(bear, color=na if bear == 0 else bear_css)
    plot2 = plot(0, color=na, editable=False)
    hline(50, 'Midline')
    fill(plot0, plot2, color=bull_grad)
    fill(plot1, plot2, color=bear_grad)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
