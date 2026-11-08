"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    alertcondition, close, color, high, input, location, low, math, na, nz,
    open, plot, plotshape, script, shape, size, ta
)
from pynecore.types import NA, Series


@script.indicator(title='Exhaustion levels (InSilico)', shorttitle='LeveLeledc (InSilico)', overlay=True, na_bool=True)
def main(
    exhaustionSwitch=input(True, title='Show exhaustion Bar point (Arrows)'),
    levelSwitch=input(True, title='Show exhaustion levels (Lines)'),
    length=input(40, 'Exhaustions swing length'),
    bars=input(10, 'Exhaustion bar count'),
    thicknesSwitch=input(2, title='Line Thickness(Level thickness)')
):
    def Lelec(bars, len):
        bindex: Series = NA(int)
        bindex = nz(bindex[1], 0)
        sindex: Series = NA(int)
        sindex = nz(sindex[1], 0)
        return_1: int = 0
        bindex = bindex + 1 if close > close[4] else bindex
        sindex = sindex + 1 if close < close[4] else sindex
        highest_1 = ta.highest(high, len)
        __block_result__ = na
        if bindex > bars and close < open and (high >= highest_1):
            bindex = 0
            return_1 = -1
            __block_result__ = return_1
        else:
            lowest_1 = ta.lowest(low, len)
            __block_result_1__ = na
            if sindex > bars and close > open and (low <= lowest_1):
                sindex = 0
                return_1 = 1
                __block_result_1__ = return_1
            __block_result__ = __block_result_1__
        return __block_result__

    Lelex = Lelec(bars, length)
    highlel = high if Lelex == -1 else na
    lowlel = low if Lelex == 1 else na
    resistance: Series = NA(float)
    support: Series = NA(float)
    resistance = high if close < open and Lelex else resistance[1]
    support = low if close > open and Lelex else support[1]
    rescol = color.new(color.new('#FF0000'), 1)
    highcol = rescol if ta.change(resistance) == 0 else na
    supcol = color.new(color.new('#138484'), 1)
    lowcol = supcol if ta.change(support) == 0 else na
    plotshape(lowlel if exhaustionSwitch else na, title='Up', color=color.new(color.new('#00FF00'), 1), location=location.belowbar, style=shape.triangleup, size=size.normal)
    plotshape(highlel if exhaustionSwitch else na, title='Down', color=color.new(color.new('#FF0000'), 1), location=location.abovebar, style=shape.triangledown, size=size.normal)
    plot(resistance if levelSwitch else na, title='Reistance Level', style=plot.style_line, color=highcol, linewidth=math.max(1, thicknesSwitch))
    plot(support if levelSwitch else na, title='Support Level', style=plot.style_line, color=lowcol, linewidth=math.max(1, thicknesSwitch))
    alertcondition(cast_bool(lowlel), 'Up')
    alertcondition(cast_bool(highlel), 'Down')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
