"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import close, color, high, input, low, math, na, plot, script, strategy, ta
from pynecore.types import Series


@script.strategy('Nadaraya-Watson Envelope Strategy', overlay=True, pyramiding=1, default_qty_type=strategy.percent_of_equity, default_qty_value=20, margin_long=0, margin_short=0, initial_capital=1000000, close_by_id=True)
def main(
    customLookbackWindow=input.int(8, 'Lookback Window (Custom)', group='Custom Settings'),
    customRelativeWeighting=input.float(8.0, 'Relative Weighting (Custom)', step=0.25, group='Custom Settings'),
    customStartRegressionBar=input.int(25, 'Start Regression at Bar (Custom)', group='Custom Settings'),
    customATRLength=input.int(60, 'ATR Length (Custom)', minval=1, group='Custom Settings'),
    customNearATRFactor=input.float(1.5, 'Near ATR Factor (Custom)', minval=0.5, step=0.25, group='Custom Settings'),
    customFarATRFactor=input.float(2.0, 'Far ATR Factor (Custom)', minval=1.0, step=0.25, group='Custom Settings'),
    strategyType=input.string('Long Only', title='Strategy Type', options=('Long Only', 'Long/Short'), group='Custom Settings')
):
    def getEnvelopeBounds(_atr, _nearFactor, _farFactor, _envelope):
        _upperFar = _envelope + _farFactor * _atr
        _upperNear = _envelope + _nearFactor * _atr
        _lowerNear = _envelope - _nearFactor * _atr
        _lowerFar = _envelope - _farFactor * _atr
        _upperAvg = (_upperFar + _upperNear) / 2
        _lowerAvg = (_lowerFar + _lowerNear) / 2
        return (_upperNear, _upperFar, _upperAvg, _lowerNear, _lowerFar, _lowerAvg)

    def customATR(length, _high: Series, _low, _close: Series):
        trueRange = math.log(_high) - math.log(_low) if na(_high[1]) else math.max(math.max(math.log(_high) - math.log(_low), math.abs(math.log(_high) - math.log(_close[1]))), math.abs(math.log(_low) - math.log(_close[1])))
        return ta.rma(trueRange, length)

    def customKernel(x: Series, h, alpha, x_0):
        sumWeights: float = 0.0
        sumXWeights: float = 0.0
        for i in pine_range(0, h, 1):
            weight = math.pow(1 + math.pow(x_0 - i, 2) / (2 * alpha * h * h), -alpha)
            sumWeights = sumWeights + weight
            sumXWeights = sumXWeights + weight * x[i]
        return sumXWeights / sumWeights

    customEnvelopeClose = math.exp(customKernel(math.log(close), customLookbackWindow, customRelativeWeighting, customStartRegressionBar))
    customEnvelopeHigh = math.exp(customKernel(math.log(high), customLookbackWindow, customRelativeWeighting, customStartRegressionBar))
    customEnvelopeLow = math.exp(customKernel(math.log(low), customLookbackWindow, customRelativeWeighting, customStartRegressionBar))
    plot(customEnvelopeHigh, color=color.red, title='Custom Envelope High')
    plot(customEnvelopeLow, color=color.teal, title='Custom Envelope Low')
    customATR__global__ = customATR(customATRLength, customEnvelopeHigh, customEnvelopeLow, customEnvelopeClose)
    customUpperNear, customUpperFar, customUpperAvg, customLowerNear, customLowerFar, customLowerAvg = getEnvelopeBounds(customATR__global__, customNearATRFactor, customFarATRFactor, math.log(customEnvelopeClose))
    if strategyType == 'Long Only':
        longCondition = ta.crossover(close, customEnvelopeLow)
        if longCondition:
            strategy.entry('Buy', strategy.long)
        exitLongCondition = ta.crossover(customEnvelopeHigh, close)
        if exitLongCondition:
            strategy.close('Buy')
    if strategyType == 'Long/Short':
        longCondition = ta.crossover(close, customEnvelopeLow)
        shortCondition = ta.crossunder(close, customEnvelopeHigh)
        if longCondition:
            strategy.entry('Buy', strategy.long)
        if shortCondition:
            strategy.entry('Sell', strategy.short)
        exitLongCondition = ta.crossover(customEnvelopeHigh, close)
        exitShortCondition = ta.crossunder(customEnvelopeLow, close)
        if exitLongCondition:
            strategy.close('Buy')
        if exitShortCondition:
            strategy.close('Sell')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)