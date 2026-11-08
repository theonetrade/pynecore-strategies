"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    alertcondition, close, color, high, input, location, low, plotshape,
    script, shape, size
)
from pynecore.types import Persistent, PersistentSeries


@script.indicator('Reversal', overlay=True, na_bool=True)
def main(
    lookback=input.int(defval=20, title='Candle Lookback'),
    confirmation=input.int(defval=3, title='Confirm Within'),
    nonRepaint=input.bool(defval=False, title='Non-Repainting Mode')
):
    bullCandle: int = 0
    bearCandle: int = 0
    vup: bool = False
    vdn: bool = False
    bullActiveCandle: PersistentSeries[bool] = False
    bullActiveCandleLow: Persistent[float] = 0.0
    bullActiveCandleHigh: PersistentSeries[float] = 0.0
    bullSignalActive: PersistentSeries[bool] = False
    bullCandleCount: PersistentSeries[int] = 0
    bearActiveCandle: PersistentSeries[bool] = False
    bearActiveCandleLow: PersistentSeries[float] = 0.0
    bearActiveCandleHigh: Persistent[float] = 0.0
    bearSignalActive: PersistentSeries[bool] = False
    bearCandleCount: PersistentSeries[int] = 0
    for i in pine_range(0, lookback - 1, 1):
        if close < low[i]:
            bullCandle = bullCandle + 1
        if close > high[i]:
            bearCandle = bearCandle + 1
    if bullCandle == lookback - 1:
        bullActiveCandle = True
        bullActiveCandleLow = low
        bullActiveCandleHigh = high
        bullSignalActive = False
        bullCandleCount = 0
    if bullActiveCandle:
        bullCandleCount = bullCandleCount + 1
    if bearCandle == lookback - 1:
        bearActiveCandle = True
        bearActiveCandleLow = low
        bearActiveCandleHigh = high
        bearSignalActive = False
        bearCandleCount = 0
    if bearActiveCandle:
        bearCandleCount = bearCandleCount + 1
    if close < bullActiveCandleLow:
        bullActiveCandle = False
    if close > bearActiveCandleHigh:
        bearActiveCandle = False
    if nonRepaint:
        if bullActiveCandle[1] == True and close[1] > bullActiveCandleHigh[1] and (bullSignalActive[1] == False) and (bullCandleCount[1] <= confirmation + 1):
            bullSignalActive = True
            vup = True
    elif bullActiveCandle == True and close > bullActiveCandleHigh and (bullSignalActive == False) and (bullCandleCount <= confirmation + 1):
        bullSignalActive = True
        vup = True
    if nonRepaint:
        if bearActiveCandle[1] == True and close[1] < bearActiveCandleLow[1] and (bearSignalActive[1] == False) and (bearCandleCount[1] <= confirmation + 1):
            bearSignalActive = True
            vdn = True
    elif bearActiveCandle == True and close < bearActiveCandleLow and (bearSignalActive == False) and (bearCandleCount <= confirmation + 1):
        bearSignalActive = True
        vdn = True
    plotshape(vup, title='V Up', style=shape.triangleup, location=location.belowbar, color=color.lime, size=size.small)
    plotshape(vdn, title='V Dn', style=shape.triangledown, location=location.abovebar, color=color.red, size=size.small)
    alertcondition(vup, 'Bullish Revarsal', 'Bullish Revarsal')
    alertcondition(vdn, 'Bearish Revarsal', 'Bearish Revarsal')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
