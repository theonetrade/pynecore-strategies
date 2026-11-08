"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_int
from pynecore.lib import (
    alertcondition, barcolor, close, color, fill, input, math, na, plot,
    request, script, syminfo, ta
)
from pynecore.types import Series


@script.indicator('Hull Suite by InSilico', overlay=True, na_bool=True)
def main(
    src: Series[float] = input(close, title='Source'),
    modeSwitch=input.string('Hma', title='Hull Variation', options=('Hma', 'Thma', 'Ehma')),
    length=input(55, title='Length(180-200 for floating S/R , 55 for swing entry)'),
    lengthMult=input(1.0, title='Length multiplier (Used to view higher timeframes with straight band)'),
    useHtf=input(False, title='Show Hull MA from X timeframe? (good for scalping)'),
    htf=input.timeframe('240', title='Higher timeframe'),
    switchColor=input(True, 'Color Hull according to trend?'),
    candleCol=input(False, title='Color candles based on Hull\'s Trend?'),
    visualSwitch=input(True, title='Show as a Band?'),
    thicknesSwitch=input(1, title='Line Thickness'),
    transpSwitch=input.int(40, title='Band Transparency', step=5)
):
    def HMA(_src, _length):
        return ta.wma(2 * ta.wma(_src, _length / 2) - ta.wma(_src, _length), math.round(math.sqrt(_length)))

    def EHMA(_src, _length):
        return ta.ema(2 * ta.ema(_src, _length / 2) - ta.ema(_src, _length), math.round(math.sqrt(_length)))

    def THMA(_src, _length):
        return ta.wma(ta.wma(_src, _length / 3) * 3 - ta.wma(_src, _length / 2) - ta.wma(_src, _length), _length)

    def Mode(modeSwitch, src, len):
        return HMA(src, len) if modeSwitch == 'Hma' else EHMA(src, len) if modeSwitch == 'Ehma' else THMA(src, len / 2) if modeSwitch == 'Thma' else na

    _hull = Mode(modeSwitch, src, cast_int(length * lengthMult))
    HULL: Series = request.security(syminfo.ticker, htf, _hull) if useHtf else _hull
    MHULL = HULL
    SHULL = HULL[2]
    hullColor = (color.new('#00FF00') if HULL > HULL[2] else color.new('#FF0000')) if switchColor else color.new('#FF9800')
    Fi1 = plot(MHULL, title='MHULL', color=hullColor, linewidth=math.max(1, thicknesSwitch))
    Fi2 = plot(SHULL if visualSwitch else na, title='SHULL', color=hullColor, linewidth=math.max(1, thicknesSwitch))
    alertcondition(ta.crossover(MHULL, SHULL), title='Hull trending up.', message='Hull trending up.')
    alertcondition(ta.crossover(SHULL, MHULL), title='Hull trending down.', message='Hull trending down.')
    fill(Fi1, Fi2, title='Band Filler', color=color.new(hullColor, transpSwitch))
    barcolor(color=(hullColor if switchColor else na) if candleCol else na)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
