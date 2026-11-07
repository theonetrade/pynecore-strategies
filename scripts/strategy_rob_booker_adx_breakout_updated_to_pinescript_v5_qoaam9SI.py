"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.series import inline_series
from pynecore.lib import (
    bgcolor, close, color, fixnan, high, input, low, math, na, plot, script,
    strategy, ta
)
from pynecore.types import Persistent


@script.strategy('Rob Booker - ADX Breakout', shorttitle='ADX Breakout V5', overlay=True, default_qty_type=strategy.cash, default_qty_value=100000, initial_capital=100000, margin_long=0, margin_short=0, close_by_id=True)
def main(
    adxSmoothPeriod=input(14, title='ADX Smoothing Period', group='ADX Settings'),
    adxPeriod=input(14, title='ADX Period', group='ADX Settings'),
    adxLowerLevel=input(18, title='ADX Lower Level', group='ADX Settings'),
    boxLookBack=input(20, title='BreakoutBox Lookback Period', group='BreakoutBox'),
    profitTargetMultiple=input(1.0, title='Profit Target Box Width Multiple', group='Take Profit and Stop Loss'),
    stopLossMultiple=input(0.5, title='Stop Loss Box Width Multiple', group='Take Profit and Stop Loss'),
    enableDirection=input(0, title='Both(0), Long(1), Short(-1)', group='Trade Direction')
):
    def dirmov(len):
        up = ta.change(high)
        down = -ta.change(low)
        truerange = ta.rma(ta.tr, len)
        plus = fixnan(100 * ta.rma(up if up > down and up > 0 else 0, len) / truerange)
        minus = fixnan(100 * ta.rma(down if down > up and down > 0 else 0, len) / truerange)
        return (plus, minus)

    def adx(dilen, adxlen):
        plus, minus = dirmov(dilen)
        sum = plus + minus
        adx__00000014__ = 100 * ta.rma(math.abs(plus - minus) / (1 if sum == 0 else sum), adxlen)
        return adx__00000014__

    def adxHigh(dilen, adxlen):
        plus, minus = dirmov(dilen)
        return plus

    def adxLow(dilen, adxlen):
        plus, minus = dirmov(dilen)
        return minus

    sig = adx(adxSmoothPeriod, adxPeriod)
    isADXLow = sig < adxLowerLevel
    boxUpperLevelCarry: Persistent[float] = 0
    boxLowerLevelCarry: Persistent[float] = 0
    boxUpperLevel = inline_series(ta.highest(high, boxLookBack), 1) if strategy.position_size == 0 else boxUpperLevelCarry
    boxUpperLevelCarry = boxUpperLevel
    boxLowerLevel = inline_series(ta.lowest(low, boxLookBack), 1) if strategy.position_size == 0 else boxLowerLevelCarry
    boxLowerLevelCarry = boxLowerLevel
    boxWidth = boxUpperLevel - boxLowerLevel
    profitTarget = strategy.position_avg_price + profitTargetMultiple * boxWidth if strategy.position_size > 0 else strategy.position_avg_price - profitTargetMultiple * boxWidth if strategy.position_size < 0 else na
    stopLoss = strategy.position_avg_price - stopLossMultiple * boxWidth if strategy.position_size > 0 else strategy.position_avg_price + stopLossMultiple * boxWidth if strategy.position_size < 0 else na
    plot(boxUpperLevel if strategy.position_size == 0 else na, color=color.white, style=plot.style_linebr)
    plot(boxLowerLevel if strategy.position_size == 0 else na, color=color.white, style=plot.style_linebr)
    bgcolor(color.purple if isADXLow else na, title='ADX limit')
    plot(stopLoss, color=color.red, linewidth=2, style=plot.style_linebr, title='StopLossLine')
    plot(profitTarget, color=color.blue, linewidth=2, style=plot.style_linebr, title='ProfitTargetLine')
    cross_1 = ta.cross(close, boxUpperLevel)
    isBuyValid = strategy.position_size == 0 and cross_1 and isADXLow
    strategy.exit('close_long', from_entry='open_long', limit=profitTarget, stop=stopLoss)
    if isBuyValid and strategy.opentrades == 0 and (enableDirection == -1 or enableDirection == 0):
        strategy.entry('open_long', strategy.long)
    cross_2 = ta.cross(close, boxLowerLevel)
    isSellValid = strategy.position_size == 0 and cross_2 and isADXLow
    strategy.exit(id='close_short', from_entry='open_short', limit=profitTarget, stop=stopLoss)
    if isSellValid and strategy.opentrades == 0 and (enableDirection == 1 or enableDirection == 0):
        strategy.entry('open_short', strategy.short)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
