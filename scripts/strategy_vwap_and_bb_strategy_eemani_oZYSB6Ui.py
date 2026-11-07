"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    barcolor, close, color, currency, fill, input, na, open, plot, script,
    strategy, ta
)
from pynecore.types import Series


@script.strategy(title='VWAP and BB strategy [EEMANI]', overlay=True, pyramiding=2, default_qty_value=1, default_qty_type=strategy.fixed, initial_capital=10000, currency=currency.USD, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    shortEMA=input.int(13, title='fast EMA', minval=1),
    longEMA=input.int(55, title='slow EMA', minval=1),
    smaLength=input.int(20, title='BB SMA Length', minval=1),
    bbsrc: Series[float] = input(close, title='BB Source'),
    strategyCalcOption=input.string(title='strategy to use', options=('BB', 'BB_percentageB'), defval='BB'),
    stopLoss=input.int(title='Stop Loss%', defval=5, minval=1),
    mult=input.float(2.0, minval=0.001, maxval=50, title='StdDev'),
    offset=input.int(0, 'Offset', minval=-500, maxval=500)
):
    def is_price_dipped_bb(pds, source1):
        t_bbDipped: bool = False
        for i in pine_range(1, pds, 1):
            t_bbDipped = True if t_bbDipped or close[i] < source1 else False
            if t_bbDipped == True:
                break
            else:
                continue
        return t_bbDipped

    def is_bb_per_dipped(pds, bbrSrc: Series):
        t_bbDipped: bool = False
        for i in pine_range(1, pds, 1):
            t_bbDipped = True if t_bbDipped or bbrSrc[i] <= 0 else False
            if t_bbDipped == True:
                break
            else:
                continue
        return t_bbDipped

    longEMAval = ta.ema(close, longEMA)
    shortEMAval = ta.ema(close, shortEMA)
    ema200val = ta.ema(close, 200)
    vwapVal = ta.vwap(close)
    plot(shortEMAval, color=color.new(color.green, 0), linewidth=1)
    plot(longEMAval, color=color.new(color.orange, 0), linewidth=1)
    plot(ema200val, color=color.new(color.purple, 0), linewidth=2, style=plot.style_line)
    basis = ta.sma(bbsrc, smaLength)
    dev = mult * ta.stdev(bbsrc, smaLength)
    upperBand = basis + dev
    lowerBand = basis - dev
    bbr = (bbsrc - lowerBand) / (upperBand - lowerBand)
    p1 = plot(upperBand, 'Upper', color=color.new(color.teal, 0), offset=offset)
    p2 = plot(lowerBand, 'Lower', color=color.new(color.teal, 0), offset=offset)
    fill(p1, p2, title='Background', color=color.new(color.new('#198787'), 95))
    plot(vwapVal, color=color.new(color.purple, 0), linewidth=2)
    longCondition = shortEMAval > longEMAval and close > open and (close > vwapVal) and (close < upperBand)
    is_price_dipped_bb_1 = is_price_dipped_bb(10, lowerBand)
    is_bb_per_dipped_1 = is_bb_per_dipped(10, bbr)
    if longCondition and (is_price_dipped_bb_1 if strategyCalcOption == 'BB' else is_bb_per_dipped_1) and (strategy.position_size < 1):
        strategy.entry(id='VWAP_BB LE', comment='VB LE', direction=strategy.long)
    if strategy.position_size >= 1 and close < strategy.position_avg_price and (close > vwapVal):
        strategy.entry(id='VWAP_BB LE', comment='Add', direction=strategy.long)
    barcolor(color.blue if strategy.position_size >= 1 else na)
    if ta.crossover(close, upperBand):
        strategy.close(id='VWAP_BB LE', comment='TP Exit')
    stopLossVal = strategy.position_avg_price * (1 - stopLoss * 0.01)
    if close < stopLossVal:
        strategy.close(id='VB LE', comment='SL Exit')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
