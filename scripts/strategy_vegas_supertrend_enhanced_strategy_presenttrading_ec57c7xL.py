"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    barcolor, close, color, currency, hlc3, input, location, math, na, nz,
    plot, plotshape, script, shape, strategy, ta
)
from pynecore.types import PersistentSeries


@script.strategy('Vegas SuperTrend Enhanced - strategy [presentTrading]', shorttitle='Vegas SuperTrend Enhanced - strategy [presentTrading]', overlay=True, precision=3, default_qty_type=strategy.cash, commission_value=0.1, commission_type=strategy.commission.percent, slippage=1, currency=currency.USD, default_qty_value=10000, initial_capital=10000, margin_long=0, margin_short=0, close_by_id=True)
def main(
    tradeDirectionChoice=input.string(title='Trade Direction', defval='Both', options=('Long', 'Short', 'Both')),
    atrPeriod=input(10, 'ATR Period for SuperTrend'),
    vegasWindow=input(100, 'Vegas Window Length'),
    superTrendMultiplier=input(5, 'SuperTrend Multiplier Base'),
    volatilityAdjustment=input.float(5, 'Volatility Adjustment Factor')
):
    vegasMovingAverage = ta.sma(close, vegasWindow)
    vegasChannelStdDev = ta.stdev(close, vegasWindow)
    vegasChannelUpper = vegasMovingAverage + vegasChannelStdDev
    vegasChannelLower = vegasMovingAverage - vegasChannelStdDev
    channelVolatilityWidth = vegasChannelUpper - vegasChannelLower
    adjustedMultiplier = superTrendMultiplier + volatilityAdjustment * (channelVolatilityWidth / vegasMovingAverage)
    averageTrueRange = ta.atr(atrPeriod)
    superTrendUpper = hlc3 - adjustedMultiplier * averageTrueRange
    superTrendLower = hlc3 + adjustedMultiplier * averageTrueRange
    superTrendPrevUpper: PersistentSeries[float] = na(float)
    superTrendPrevLower: PersistentSeries[float] = na(float)
    marketTrend: PersistentSeries[int] = 1
    superTrendPrevUpper = nz(superTrendPrevUpper[1], superTrendUpper)
    superTrendPrevLower = nz(superTrendPrevLower[1], superTrendLower)
    marketTrend = 1 if close > superTrendPrevLower else -1 if close < superTrendPrevUpper else nz(marketTrend[1], 1)
    superTrendUpper = math.max(superTrendUpper, superTrendPrevUpper) if marketTrend == 1 else superTrendUpper
    superTrendLower = math.min(superTrendLower, superTrendPrevLower) if marketTrend == -1 else superTrendLower
    superTrendPrevUpper = superTrendUpper
    superTrendPrevLower = superTrendLower
    plot(superTrendUpper if marketTrend == 1 else na, 'SuperTrend Upper', color=color.green, linewidth=2)
    plot(superTrendLower if marketTrend == -1 else na, 'SuperTrend Lower', color=color.red, linewidth=2)
    plot(vegasChannelUpper, 'Vegas Upper', color=color.purple, linewidth=1)
    plot(vegasChannelLower, 'Vegas Lower', color=color.purple, linewidth=1)
    barcolor(color.green if marketTrend == 1 else color.red if marketTrend == -1 else na)
    trendShiftToBullish = marketTrend == 1 and marketTrend[1] == -1
    trendShiftToBearish = marketTrend == -1 and marketTrend[1] == 1
    plotshape(series=trendShiftToBullish, title='Enter Long', location=location.belowbar, color=color.green, style=shape.labelup, text='Buy')
    plotshape(series=trendShiftToBearish, title='Enter Short', location=location.abovebar, color=color.red, style=shape.labeldown, text='Sell')
    enterLongCondition = marketTrend == 1
    enterShortCondition = marketTrend == -1
    if enterLongCondition and (tradeDirectionChoice == 'Long' or tradeDirectionChoice == 'Both'):
        strategy.entry('Long Position', strategy.long)
    if enterShortCondition and (tradeDirectionChoice == 'Short' or tradeDirectionChoice == 'Both'):
        strategy.entry('Short Position', strategy.short)
    if marketTrend != marketTrend[1]:
        strategy.close_all()


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
