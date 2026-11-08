"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, close, color, fill, hl2, input, location, math, plot,
    plotshape, script, shape, size, ta
)
from pynecore.types import Series


@script.indicator(shorttitle='BBAWE', title='Bollinger Awesome Alert R1.1 by JustUncleL', overlay=True, na_bool=True)
def main(
    bb_use_ema=input(False, title='Use EMA for Bollinger Band'),
    bb_filter=input(False, title='Filter Buy/Sell with Bollinger Bands'),
    sqz_filter=input(False, title='Flter Buy/Sell with BB squeeze'),
    bb_length=input.int(20, minval=1, title='Bollinger Length'),
    bb_source: Series[float] = input(close, title='Bollinger Source'),
    bb_mult=input.float(2.0, title='Base Multiplier', minval=0.5, maxval=10),
    fast_ma_len=input.int(3, title='Fast EMA length', minval=2),
    nLengthSlow=input.int(34, minval=1, title='Awesome Length Slow'),
    nLengthFast=input.int(5, minval=1, title='Awesome Length Fast'),
    sqz_length=input.int(100, 'BB Relative Squeeze Length', minval=5),
    sqz_threshold=input.int(50, 'BB Squeeze Threshold %', maxval=99, step=5)
):
    ema_1 = ta.ema(bb_source, bb_length)
    sma_1 = ta.sma(bb_source, bb_length)
    bb_basis = ema_1 if bb_use_ema else sma_1
    fast_ma = ta.ema(bb_source, fast_ma_len)
    dev = ta.stdev(bb_source, bb_length)
    bb_dev = bb_mult * dev
    bb_upper = bb_basis + bb_dev
    bb_lower = bb_basis - bb_dev
    xSMA1_hl2 = ta.sma(hl2, nLengthFast)
    xSMA2_hl2 = ta.sma(hl2, nLengthSlow)
    xSMA1_SMA2: Series = xSMA1_hl2 - xSMA2_hl2
    AO = (1 if xSMA1_SMA2 > xSMA1_SMA2[1] else 2) if xSMA1_SMA2 >= 0 else -1 if xSMA1_SMA2 > xSMA1_SMA2[1] else -2
    spread = bb_upper - bb_lower
    avgspread = ta.sma(spread, sqz_length)
    bb_squeeze = spread / avgspread * 100
    bb_offset = ta.atr(14) * 0.5
    bb_sqz_upper = bb_upper + bb_offset
    bb_sqz_lower = bb_lower - bb_offset
    plot(bb_basis, title='Basis Line', color=color.new(color.red, 10), linewidth=2)
    ubi = plot(bb_upper, title='Upper Band Inner', color=color.new(color.blue, 10), linewidth=1)
    lbi = plot(bb_lower, title='Lower Band Inner', color=color.new(color.blue, 10), linewidth=1)
    fill(ubi, lbi, title='Center Channel Fill', color=color.new(color.silver, 90))
    usqzi = plot(bb_sqz_upper, 'Hide Sqz Upper')
    lsqzi = plot(bb_sqz_lower, 'Hide Sqz Lower')
    fill(ubi, usqzi, color=color.new(color.white if bb_squeeze > sqz_threshold else color.blue, 50))
    fill(lbi, lsqzi, color=color.new(color.white if bb_squeeze > sqz_threshold else color.blue, 50))
    plot(fast_ma, title='Fast EMA', color=color.new(color.black, 10), linewidth=2)
    break_down = ta.crossunder(fast_ma, bb_basis) and close < bb_basis and (math.abs(AO) == 2) and (not bb_filter or close > bb_lower) and (not sqz_filter or bb_squeeze > sqz_threshold)
    break_up = ta.crossover(fast_ma, bb_basis) and close > bb_basis and (math.abs(AO) == 1) and (not bb_filter or close < bb_upper) and (not sqz_filter or bb_squeeze > sqz_threshold)
    plotshape(break_down, title='Breakout Down', style=shape.arrowdown, location=location.abovebar, size=size.auto, text='Sell', color=color.new(color.red, 0))
    plotshape(break_up, title='Breakout Up', style=shape.arrowup, location=location.belowbar, size=size.auto, text='Buy', color=color.new(color.green, 0))
    alertcondition(break_down or break_up, title='BBAWE Alert', message='BBAWE Alert close={{close}}')
    alertcondition(break_down, title='BBAWE Sell', message='SELL close={{close}}')
    alertcondition(break_up, title='BBAWE Buy', message='BUY close={{close}}')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
