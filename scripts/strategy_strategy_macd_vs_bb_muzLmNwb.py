"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, fill, input, location, na, plot, plotshape, script, shape,
    size, strategy, ta
)
from pynecore.types import Series


@script.strategy('Strategy MACD vs BB', overlay=False, pyramiding=5, default_qty_type=strategy.fixed, default_qty_value=10000, margin_long=0, margin_short=0, initial_capital=100000, close_by_id=True, na_bool=True)
def main(
    fast_length=input(title='Fast MA period', defval=8),
    slow_length=input(title='Slow MA period', defval=21),
    src: Series[float] = input(close, 'Source'),
    smoothinput=input.int(1, minval=1, maxval=4, title='Moving Average Calculation: (1 = SMA), (2 = EMA), (3 = WMA), (4 = Linear)'),
    length=input.int(40, minval=1),
    mult=input(2.0, 'BB multiplier')
):
    fast_ma = ta.sma(src, fast_length) if smoothinput == 1 else ta.ema(src, fast_length) if smoothinput == 2 else ta.wma(src, fast_length) if smoothinput == 3 else ta.linreg(src, fast_length, 0) if smoothinput == 4 else na
    slow_ma = ta.sma(src, slow_length) if smoothinput == 1 else ta.ema(src, slow_length) if smoothinput == 2 else ta.wma(src, slow_length) if smoothinput == 3 else ta.linreg(src, slow_length, 0) if smoothinput == 4 else na
    macd = fast_ma - slow_ma
    p1 = plot(macd, 'macd signal', color=color.new(color.blue, 0))
    basis = ta.sma(macd, length)
    dev = mult * ta.stdev(macd, length)
    plot(basis, 'BB basis', color=color.new(color.orange, 0))
    upper = basis + dev
    lower = basis - dev
    p2 = plot(upper, 'BB upper', color=color.new(color.red, 0))
    p3 = plot(lower, 'BB basis', color=color.new(color.green, 0))
    longCondition = ta.crossover(macd, lower)
    shortCondition = ta.crossunder(macd, upper)
    plotshape(lower if longCondition else na, title='Long', style=shape.xcross, location=location.absolute, text='Long', color=color.new(color.green, 0), size=size.tiny)
    plotshape(upper if shortCondition else na, title='Short', style=shape.xcross, location=location.absolute, text='Short', color=color.new(color.red, 0), size=size.tiny)
    fill(p1, p3, color=color.new(color.green if macd < lower else na, 90), title='support')
    fill(p1, p2, color=color.new(color.red if macd > upper else na, 90), title='resistance')
    if longCondition:
        strategy.entry('Long', strategy.long)
    if shortCondition:
        strategy.entry('Short', strategy.short)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
