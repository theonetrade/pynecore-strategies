"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, input, na, open, plot, script, ta, volume
from pynecore.types import Color


@script.indicator('Volume Flow v3', shorttitle='Volume Flow [DepthHouse]', na_bool=True)
def main(
    maType=input.string(title='Moving Average Type', options=('Simple', 'Exponential', 'Double Exponential'), defval='Simple'),
    length=input(14, title='MA Length'),
    x=input(3.1, title='Factor For Breakout Candle')
):
    red: Color = color.new('#FF510D')
    green: Color = color.new('#5AA650')
    vol = volume
    bull = vol if close > open else 0
    bear = vol if open > close else 0
    def dema(src, len):
        return 2 * ta.ema(src, len) - ta.ema(ta.ema(src, len), len)

    bullma = ta.ema(bull, length) if maType == 'Exponential' else dema(bull, length) if maType == 'Double Exponential' else ta.sma(bull, length)
    bearma = ta.ema(bear, length) if maType == 'Exponential' else dema(bear, length) if maType == 'Double Exponential' else ta.sma(bear, length)
    vf_dif = bullma - bearma
    vf_absolute = vf_dif if vf_dif > 0 else vf_dif * -1
    gsig = vol if ta.crossover(bull, bullma * x) else na
    rsig = vol if ta.crossover(bear, bearma * x) else na
    vdClr = green if vf_dif > 0 else red
    vClr = green if close > open else red
    plot(vol, color=vClr, style=plot.style_columns, title='Volume')
    plot(bullma * 2, color=color.new(green, 0), linewidth=1, title='Bull MA')
    plot(bearma * 2, color=color.new(red, 0), linewidth=1, title='Bear MA')
    plot(gsig, style=plot.style_columns, color=color.new(green, 50), title='Bull Vol Spike')
    plot(rsig, style=plot.style_columns, color=color.new(red, 50), title='Bear Vol Spike')
    plot(vf_absolute / 2.5, style=plot.style_area, color=vdClr, title='Difference Value')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
