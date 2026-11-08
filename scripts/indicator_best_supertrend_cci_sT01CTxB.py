"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, hl2, input, math, nz, plot, script, ta
from pynecore.types import Color, Series

StudyName: str = 'BEST Supertrend CCI'
ShortStudyName: str = 'BEST Supertrend CCI'


@script.indicator(StudyName, shorttitle=ShortStudyName, overlay=True, precision=6, na_bool=True)
def main(
    source: Series[float] = input(close),
    cci_period=input(28, 'CCI Period'),
    ML=input(0, 'CCI Mid Line pivot'),
    Factor=input.float(3, title='[ST] Factor', minval=1, maxval=100),
    Pd=input.int(3, title='[ST] PD', minval=1, maxval=100)
):
    AQUA: Color = color.new('#00FFFF')
    BLUE: Color = color.new('#0000FF')
    RED: Color = color.new('#FF0000')
    LIME: Color = color.new('#00FF00')
    GRAY: Color = color.new('#808080')
    DARKRED: Color = color.new('#8B0000')
    DARKGREEN: Color = color.new('#006400')
    GOLD: Color = color.new('#FFD700')
    WHITE = color.white
    GREEN_LIGHT = color.new(color.green, 40)
    RED_LIGHT = color.new(color.red, 40)
    BLUE_LIGHT = color.new(color.aqua, 40)
    PURPLE_LIGHT = color.new(color.purple, 40)
    cci: Series = ta.cci(source, cci_period)
    def f_supertrend(Factor, Pd):
        __hist_cci__: Series = cci[0]
        Up = hl2 - Factor * ta.atr(Pd)
        Dn = hl2 + Factor * ta.atr(Pd)
        TrendUp: Series[float] = 0.0
        TrendUp = math.max(Up, TrendUp[1]) if __hist_cci__[1] > ML else Up
        TrendDown: Series[float] = 0.0
        TrendDown = math.min(Dn, TrendDown[1]) if __hist_cci__[1] < ML else Dn
        Trend: Series[float] = 0.0
        Trend = 1 if cci > ML else -1 if cci < ML else nz(Trend[1], 1)
        Tsl = TrendUp if Trend == 1 else TrendDown
        return Tsl

    st_tsl = f_supertrend(Factor, Pd)
    linecolor = color.green if close >= st_tsl else color.red
    plot(st_tsl, color=linecolor, linewidth=4, title='SuperTrend')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
