"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    barcolor, bgcolor, close, color, high, input, low, na, plot, script,
    strategy, ta
)


@script.strategy('Fractal Breakout Strategy', overlay=True, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    Barcolor=input(True, title='Barcolor'),
    Bgcolor=input(True, title='Bgcolor')
):
    FUp = high[4] < high[2] and high[3] < high[2] and (high[1] < high[2]) and (high < high[2]) or (high[5] < high[2] and high[4] < high[2] and (high[3] <= high[2]) and (high[1] < high[2]) and (high < high[2])) or (high[6] < high[2] and high[5] < high[2] and (high[4] <= high[2]) and (high[3] <= high[2]) and (high[1] < high[2]) and (high < high[2])) or (high[7] < high[2] and high[6] < high[2] and (high[5] <= high[2]) and (high[4] <= high[2]) and (high[3] <= high[2]) and (high[1] < high[2]) and (high < high[2])) or (high[8] < high[2] and high[7] < high[2] and (high[6] <= high[2]) and (high[5] <= high[2]) and (high[4] <= high[2]) and (high[3] <= high[2]) and (high[1] < high[2]) and (high < high[2]))
    FractalUp = ta.valuewhen(FUp, high[2], 1)
    plot(FractalUp, color=color.new(color.new('#0000FF'), 0), title='FractalUp')
    FDown = low[4] > low[2] and low[3] > low[2] and (low[1] > low[2]) and (low > low[2]) or (low[5] > low[2] and low[4] > low[2] and (low[3] >= low[2]) and (low[1] > low[2]) and (low > low[2])) or (low[6] > low[2] and low[5] > low[2] and (low[4] >= low[2]) and (low[3] >= low[2]) and (low[1] > low[2]) and (low > low[2])) or (low[7] > low[2] and low[6] > low[2] and (low[5] >= low[2]) and (low[4] >= low[2]) and (low[3] >= low[2]) and (low[1] > low[2]) and (low > low[2])) or (low[8] > low[2] and low[7] > low[2] and (low[6] >= low[2]) and (low[5] >= low[2]) and (low[4] >= low[2]) and (low[3] >= low[2]) and (low[1] > low[2]) and (low > low[2]))
    FractalDown = ta.valuewhen(FDown, low[2], 1)
    plot(FractalDown, color=color.new(color.new('#FF0000'), 0), title='FractalDown')
    if ta.crossover(close, FractalUp):
        strategy.entry('Long', strategy.long, comment='Long')
    if ta.crossunder(close, FractalDown):
        strategy.entry('Short', strategy.short, comment='Short')
    iff_1 = color.new('#FFFF00') if FractalDown < close else color.new('#FF0000')
    colors = color.new('#008000') if close > FractalUp else iff_1
    barcolor(colors if Barcolor else na)
    bgcolor(colors if Bgcolor else na)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
