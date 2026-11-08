"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.core.series import inline_series
from pynecore.lib import (
    alertcondition, close, color, fixnan, high, input, location, low, na,
    open, plot, plotshape, script, shape, size, ta, volume
)


@script.indicator(title=' Support and Resistance Levels with Breaks', shorttitle=' Support and Resistance Levels with Breaks [LuxAlgo]', overlay=True, max_bars_back=1000, na_bool=True)
def main(
    toggleBreaks=input(True, title='Show Breaks'),
    leftBars=input(15, title='Left Bars '),
    rightBars=input(15, title='Right Bars'),
    volumeThresh=input(20, title='Volume Threshold')
):
    highUsePivot = fixnan(inline_series(ta.pivothigh(leftBars, rightBars), 1))
    lowUsePivot = fixnan(inline_series(ta.pivotlow(leftBars, rightBars), 1))
    r1 = plot(highUsePivot, color=na if cast_bool(ta.change(highUsePivot)) else color.new('#FF0000'), linewidth=3, offset=-(rightBars + 1), title='Resistance')
    s1 = plot(lowUsePivot, color=na if cast_bool(ta.change(lowUsePivot)) else color.new('#233DEE'), linewidth=3, offset=-(rightBars + 1), title='Support')
    short = ta.ema(volume, 5)
    long = ta.ema(volume, 10)
    osc = 100 * (short - long) / long
    crossunder_1 = ta.crossunder(close, lowUsePivot)
    plotshape(toggleBreaks and crossunder_1 and (not open - close < high - open) and (osc > volumeThresh), title='Break', text='B', style=shape.labeldown, location=location.abovebar, color=color.new(color.red, 0), textcolor=color.new(color.white, 0), size=size.tiny)
    crossover_1 = ta.crossover(close, highUsePivot)
    plotshape(toggleBreaks and crossover_1 and (not open - low > close - open) and (osc > volumeThresh), title='Break', text='B', style=shape.labelup, location=location.belowbar, color=color.new(color.green, 0), textcolor=color.new(color.white, 0), size=size.tiny)
    crossover_2 = ta.crossover(close, highUsePivot)
    plotshape(toggleBreaks and crossover_2 and (open - low > close - open), title='Break', text='Bull Wick', style=shape.labelup, location=location.belowbar, color=color.new(color.green, 0), textcolor=color.new(color.white, 0), size=size.tiny)
    crossunder_2 = ta.crossunder(close, lowUsePivot)
    plotshape(toggleBreaks and crossunder_2 and (open - close < high - open), title='Break', text='Bear Wick', style=shape.labeldown, location=location.abovebar, color=color.new(color.red, 0), textcolor=color.new(color.white, 0), size=size.tiny)
    alertcondition(ta.crossunder(close, lowUsePivot) and osc > volumeThresh, title='Support Broken', message='Support Broken')
    alertcondition(ta.crossover(close, highUsePivot) and osc > volumeThresh, title='Resistance Broken', message='Resistance Broken')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
