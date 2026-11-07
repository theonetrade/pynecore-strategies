"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_import import shadowed_namespace
from pynecore.lib import (
    close, color, high, input, location, low, na, plot, plotshape, request,
    script, shape, size, strategy, ta, ticker, time, timeframe
)
from pynecore.types import PersistentSeries, Series
import lib.TradingView.ta.v7 as ta__ren____lib


ta__ren__ = shadowed_namespace(ta__ren____lib, ta)


@script.strategy('Opening Range Breakout (ORB) Heikin Ashi SPY 5min Correlation Strategy', overlay=True, margin_long=0, margin_short=0, initial_capital=1000000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    anchorTimeframeInput=input.timeframe('W', 'Anchor Timeframe', tooltip='When Chart Timeframe >= `Anchor Timeframe`, the indicator will use last `Length` bars in its calculations.', group='RVOL parameters'),
    lengthInput=input.int(3, 'Length', minval=1, group='RVOL parameters'),
    sessionTime=input.session('0930-1000', 'Session Time Opening', group='Time Session'),
    sessionTradingTime=input.session('1000-1200', 'Session Time Trading', group='Time Session'),
    sessionEndTime=input.session('1550-1555', 'Session Time Ending', group='Time Session'),
    useHeikinAshi=input(False, 'Use Heikin Ashi?', group='Correlation Parameters'),
    asset_correlation=input.symbol('SPY', group='Correlation Parameters', title='Symbol used for Correlation')
):
    currentVolume, pastVolume, _ = ta__ren__.relativeVolume(lengthInput, anchorTimeframeInput, True)
    inSession: Series = not na(time(timeframe.period, sessionTime + ':1234567'))
    inTradingSession = not na(time(timeframe.period, sessionTradingTime + ':1234567'))
    endSession = not na(time(timeframe.period, sessionEndTime + ':1234567'))
    high_ = request.security(ticker.heikinashi(asset_correlation), timeframe.period, high) if useHeikinAshi else request.security(asset_correlation, timeframe.period, high)
    low_ = request.security(ticker.heikinashi(asset_correlation), timeframe.period, low) if useHeikinAshi else request.security(asset_correlation, timeframe.period, low)
    prevSessionHigh: PersistentSeries[float] = na(float)
    prevSessionLow: PersistentSeries[float] = na(float)
    if inSession and (not inSession[1]):
        prevSessionHigh = high_
        prevSessionLow = low_
    currentSessionHigh = prevSessionHigh[1]
    currentSessionLow = prevSessionLow[1]
    if high_ > currentSessionHigh and inSession:
        currentSessionHigh = high_
    if low_ < currentSessionLow and inSession:
        currentSessionLow = low_
    plot(currentSessionHigh, color=color.green, title='ORB High', linewidth=2)
    plot(currentSessionLow, color=color.red, title='ORB Low', linewidth=2)
    longCondition = close > currentSessionHigh and inTradingSession
    shortCondition = close < currentSessionLow and inTradingSession
    longTrade: PersistentSeries[bool] = na(bool)
    shortTrade: PersistentSeries[bool] = na(bool)
    rvol = currentVolume / pastVolume
    if longCondition and (not shortTrade) and (rvol > 1):
        longTrade = True
    if shortCondition and (not longTrade) and (rvol > 1):
        shortTrade = True
    if endSession:
        longTrade = na
        shortTrade = na
    plotshape((na if na(endSession) else 1 if endSession else 0) if longTrade[1] or shortTrade[1] else na, style=shape.labeldown, location=location.abovebar, color=color.new(color.purple, 0), size=size.tiny, title='EXIT', text='END SESSION', textcolor=color.new(color.white, 0))
    if longTrade:
        strategy.entry('long', strategy.long)
    if shortTrade:
        strategy.entry('short', strategy.short)
    if endSession:
        strategy.close_all()


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
