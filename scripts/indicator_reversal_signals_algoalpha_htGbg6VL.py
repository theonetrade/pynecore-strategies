"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    alertcondition, bar_index, chart, close, color, display, fill, high,
    input, location, low, math, na, open, plot, plotshape, script, shape, size, ta, volume
)
from pynecore.types import Persistent


@script.indicator('Reversal Signals [AlgoAlpha]', 'AlgoAlpha - Reversal Signals', overlay=True)
def main(
    lookbackPeriod=input.int(defval=12, title='Candle Lookback', tooltip='Number of candles to look back for reversal detection', group='Reversal Detection Settings'),
    confirmationPeriod=input.int(defval=3, title='Confirm Within', tooltip='Number of candles within which the reversal must be confirmed', group='Reversal Detection Settings'),
    enableVolumeConfirmation=input.bool(defval=True, title='Use Volume Confirmation', tooltip='Enable or disable volume confirmation for signals', group='Reversal Detection Settings'),
    trendMAPeriod=input.int(defval=50, title='Trend MA Period', tooltip='Period for the moving average used in trend detection', group='Trend Settings'),
    trendMAType=input.string(defval='EMA', title='MA Type', options=('SMA', 'EMA', 'WMA', 'VWMA'), tooltip='Type of moving average to use', group='Trend Settings'),
    maStepPeriod=input.int(defval=33, title='MA Step Period', tooltip='Number of bars after which the stepped MA updates', group='Trend Settings'),
    bullColor=input.color(color.new('#00FFBB'), title='Bullish Color', tooltip='Color used for bullish signals and trends', group='Appearance'),
    bearColor=input.color(color.new('#FF1100'), title='Bearish Color', tooltip='Color used for bearish signals and trends', group='Appearance'),
    fill__ren__=input.bool(True, 'Trend Fill', tooltip='Enable/disable trend fills', group='Appearance'),
    steps=input.bool(True, 'MA Steps', tooltip='Enable/disable MA steps', group='Appearance')
):
    bullCandleScore: Persistent[int] = 0
    bearCandleScore: Persistent[int] = 0
    bullSignal: bool = False
    bearSignal: bool = False
    bullReversalCandidate: Persistent[bool] = False
    bearReversalCandidate: Persistent[bool] = False
    bullReversalLow: Persistent[float] = 0.0
    bullReversalHigh: Persistent[float] = 0.0
    bearReversalLow: Persistent[float] = 0.0
    bearReversalHigh: Persistent[float] = 0.0
    bullSignalConfirmed: Persistent[bool] = False
    bearSignalConfirmed: Persistent[bool] = False
    bullCandleCounter: Persistent[int] = 0
    bearCandleCounter: Persistent[int] = 0
    volumeIsHigh = volume > ta.sma(volume, 20)
    __block_result__ = na
    __switch__ = trendMAType
    if __switch__ == 'SMA':
        __block_result__ = ta.sma(close, trendMAPeriod)
    elif __switch__ == 'EMA':
        __block_result__ = ta.ema(close, trendMAPeriod)
    elif __switch__ == 'WMA':
        __block_result__ = ta.wma(close, trendMAPeriod)
    elif __switch__ == 'VWMA':
        __block_result__ = ta.vwma(close, trendMAPeriod)
    ma_current = __block_result__
    steppedMAValue: Persistent[float] = na(float)
    maLastUpdateBar: Persistent[int] = 0
    maDirection: Persistent[int] = 1
    if na(steppedMAValue):
        steppedMAValue = ma_current
        maLastUpdateBar = bar_index
    else:
        if maDirection == 1:
            if close < steppedMAValue:
                maDirection = -1
                steppedMAValue = ma_current
                maLastUpdateBar = bar_index
            elif bar_index - maLastUpdateBar >= maStepPeriod:
                newMAValue = ma_current
                steppedMAValue = math.max(steppedMAValue, newMAValue)
                maLastUpdateBar = bar_index
        else:
            if close > steppedMAValue:
                maDirection = 1
                steppedMAValue = ma_current
                maLastUpdateBar = bar_index
            elif bar_index - maLastUpdateBar >= maStepPeriod:
                newMAValue = ma_current
                steppedMAValue = math.min(steppedMAValue, newMAValue)
                maLastUpdateBar = bar_index
    bullCandleScore = 0
    bearCandleScore = 0
    for i in pine_range(0, lookbackPeriod - 1, 1):
        if close < low[i]:
            bullCandleScore = bullCandleScore + 1
        if close > high[i]:
            bearCandleScore = bearCandleScore + 1
    if bearCandleScore == lookbackPeriod - 1:
        bearReversalCandidate = True
        bearReversalLow = low
        bearReversalHigh = high
        bearSignalConfirmed = False
        bearCandleCounter = 0
    if bearReversalCandidate:
        bearCandleCounter = bearCandleCounter + 1
        if close > bearReversalHigh:
            bearReversalCandidate = False
    bearCondition: bool = False
    if bearReversalCandidate and close < bearReversalLow and (not bearSignalConfirmed) and (bearCandleCounter <= confirmationPeriod + 1):
        bearSignalConfirmed = True
        bearCondition = True
    if bearCondition:
        if not enableVolumeConfirmation or volumeIsHigh:
            bearSignal = True
    if bullCandleScore == lookbackPeriod - 1:
        bullReversalCandidate = True
        bullReversalLow = low
        bullReversalHigh = high
        bullSignalConfirmed = False
        bullCandleCounter = 0
    if bullReversalCandidate:
        bullCandleCounter = bullCandleCounter + 1
        if close < bullReversalLow:
            bullReversalCandidate = False
    bullCondition: bool = False
    if bullReversalCandidate and close > bullReversalHigh and (not bullSignalConfirmed) and (bullCandleCounter <= confirmationPeriod + 1):
        bullSignalConfirmed = True
        bullCondition = True
    if bullCondition:
        if not enableVolumeConfirmation or volumeIsHigh:
            bullSignal = True
    plotshape(bullSignal, title='Buy Signal', style=shape.labelup, location=location.belowbar, color=bullColor, size=size.small, text='𝓡', textcolor=chart.bg_color)
    plotshape(bearSignal, title='Sell Signal', style=shape.labeldown, location=location.abovebar, color=bearColor, size=size.small, text='𝓡', textcolor=chart.bg_color)
    stma = plot(steppedMAValue, title='Stepped MA', color=bullColor if close > steppedMAValue else bearColor, linewidth=2, display=display.all if steps else display.none)
    cm = plot((open + close) / 2, title='Center Line', display=display.none)
    fill(stma, cm, steppedMAValue, (open + close) / 2, color.new(bullColor, 70) if steppedMAValue < close else na, color.new(bullColor, 100) if steppedMAValue < close else na, display=display.all if fill__ren__ else display.none)
    fill(stma, cm, (open + close) / 2, steppedMAValue, color.new(bearColor, 100) if steppedMAValue > close else na, color.new(bearColor, 70) if steppedMAValue > close else na, display=display.all if fill__ren__ else display.none)
    alertcondition(bullSignal, 'Bullish Reversal', 'Bullish Reversal Signal Detected')
    alertcondition(bearSignal, 'Bearish Reversal', 'Bearish Reversal Signal Detected')
    alertcondition(ta.crossover(close, steppedMAValue), 'Bullish Trend', 'Bullish Trend Shift')
    alertcondition(ta.crossunder(close, steppedMAValue), 'Bearish Trend', 'Bearish Trend Shift')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
