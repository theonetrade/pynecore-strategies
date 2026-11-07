"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, display, fill, high, input, low, na, plot, script,
    strategy, ta
)
from pynecore.types import Persistent
import lib.HeWhoMustNotBeNamed.ta.v1 as eta


@script.strategy('PercentX Trend Follower [Trendoscope]', shorttitle='pX-TF [Trendoscope]', overlay=False, initial_capital=100000, default_qty_type=strategy.percent_of_equity, default_qty_value=10, commission_type=strategy.commission.percent, pyramiding=4, commission_value=0.01, explicit_plot_zorder=True, margin_long=100.0, margin_short=100.0, max_bars_back=5000, close_by_id=True)
def main(
    bandType=input.string('Keltner Channel', '', options=('Keltner Channel', 'Bollinger Bands'), tooltip='Select the band type', group='Band', inline='ma', display=display.none),
    maType=input.string(title='', defval='hma', options=('ema', 'sma', 'hma', 'rma', 'vwma', 'wma'), group='Band', inline='ma', display=display.none),
    maLength=input.int(40, '', minval=5, step=10, group='Band', inline='ma', display=display.none),
    useTrueRange=input.bool(True, 'Use True Range (KC)', tooltip='Use true range - applicable only for Keltner Channel', group='Band', display=display.none),
    rangeMethod=input.string('highlow', title='', group='Range Calculation', options=('highlow', 'sma', 'ema', 'rma', 'hma', 'wma', 'vwma', 'swma'), inline='l', display=display.none),
    loopbackPeriod=input.int(80, step=10, title='', group='Range Calculation', inline='l', display=display.none),
    loopbackPeriodLast=input.int(20, step=10, title='', group='Range Calculation', inline='l', display=display.none, tooltip='Range Calculation method, length and range length'),
    stickyBorders=input.bool(True, title='Sticky Borders', group='Range Calculation', inline='b', display=display.none),
    outerRangeMethod=input.string('highlow', title='', group='Outer Range Calculation', options=('highlow', 'sma', 'ema', 'rma', 'hma', 'wma', 'vwma', 'swma'), inline='l', display=display.none),
    outerLoopback=input.int(80, step=10, title='', group='Outer Range Calculation', inline='l', display=display.none, tooltip='Method and length for calculating outer range. Outer range is extreme of oversold and overbought ranges'),
    doubleSided=input.bool(True, 'Double Sided', group='Trade', display=display.none),
    useInitialStop=input.bool(True, 'Enable Stop', group='Trade', inline='s', display=display.none),
    atrLength=input.int(14, '', minval=1, step=10, group='Trade', inline='s', display=display.none),
    trendMultiplier=input.int(1, '', minval=1, maxval=10, step=1, group='Trade', inline='s', display=display.none),
    reverseMultiplier=input.int(3, '', minval=1, maxval=10, step=1, group='Trade', inline='s', tooltip='Enable Stop and Configure ATR length, Trend and reverse Multiplier for the stop', display=display.none),
    tradeDirection=input.string(strategy.direction.all, 'Direction', options=(strategy.direction.long, strategy.direction.short, strategy.direction.all), display=display.none)
):
    strategy.risk.allow_entry_in(tradeDirection)
    bbMiddle, bbUpper, bbLower = eta.bb(close, maType, maLength, 0.01, False)
    kcMiddle, kcUpper, kcLower = eta.kc(close, maType, maLength, 0.01, useTrueRange, False)
    middle = bbMiddle if bandType == 'Bollinger Bands' else kcMiddle
    upper = bbUpper if bandType == 'Bollinger Bands' else kcUpper
    lower = bbLower if bandType == 'Bollinger Bands' else kcLower
    distance = close - middle
    oscillator = distance / (middle - lower)
    offset: int = 0
    overbought, oversold = eta.oscillatorRange(oscillator, rangeMethod, loopbackPeriod, loopbackPeriodLast, stickyBorders)
    oversold = oversold + offset
    overbought = overbought - offset
    upOverflow: Persistent[bool] = False
    downOverflow: Persistent[bool] = False
    highOverboughtMa = eta.ma(overbought, outerRangeMethod, outerLoopback)
    highestOverbought = ta.highest(overbought, outerLoopback)
    lowOversoldMa = eta.ma(oversold, outerRangeMethod, outerLoopback)
    lowestOversold = ta.lowest(oversold, outerLoopback)
    upperRange = highestOverbought if outerRangeMethod == 'highlow' else highOverboughtMa
    lowerRange = lowestOversold if outerRangeMethod == 'highlow' else lowOversoldMa
    longSignal = ta.crossover(oscillator, upperRange)
    shortSignal = ta.crossunder(oscillator, lowerRange)
    upOverflow = longSignal or (upOverflow and oscillator > overbought)
    downOverflow = shortSignal or (downOverflow and oscillator < oversold)
    transparency: int = 60
    STATE = plot(oscillator, title='PercentX Oscillator', color=color.new(color.blue, 0 if upOverflow or downOverflow else transparency), style=plot.style_linebr)
    lowerBandFill = plot(oversold if downOverflow else na, 'Lower Overflow', color=color.orange, style=plot.style_linebr)
    fill(STATE, lowerBandFill, color=color.orange)
    lowerBand = plot(oversold, 'Lower', color=color.new(color.orange, 0 if downOverflow else transparency), style=plot.style_linebr)
    llowerBand = plot(lowerRange, 'Extreme Lower', color=color.new(color.red, 0 if downOverflow else transparency), style=plot.style_linebr)
    upperBandFill = plot(overbought if upOverflow else na, 'Upper Overflow', color=color.lime, style=plot.style_linebr)
    fill(STATE, upperBandFill, color=color.lime)
    upperBand = plot(overbought, 'Upper', color=color.new(color.lime, 0 if upOverflow else transparency), style=plot.style_linebr)
    uupperBand = plot(upperRange, 'Extreme Upper', color=color.new(color.green, 0 if upOverflow else transparency), style=plot.style_linebr)
    atr = ta.atr(atrLength)
    def longtrade(multiplier, stopMultiplier):
        strategy.entry('Long', strategy.long, oca_name='oca', oca_type=strategy.oca.none, stop=high + atr * multiplier, comment='Long - New Position')
        __block_result__ = na
        if useInitialStop:
            __block_result__ = strategy.exit('ExitLong', 'Long', stop=low - atr * stopMultiplier)
        return __block_result__

    def shorttrade(multiplier, stopMultiplier):
        strategy.entry('Short', strategy.short, oca_name='oca', oca_type=strategy.oca.none, stop=low - atr * multiplier, comment='Short - New Position')
        __block_result_1__ = na
        if useInitialStop:
            __block_result_1__ = strategy.exit('ExitShort', 'Short', stop=high + atr * stopMultiplier)
        return __block_result_1__

    if longSignal:
        longtrade(trendMultiplier, reverseMultiplier)
        if doubleSided:
            shorttrade(reverseMultiplier, trendMultiplier)
    if shortSignal:
        shorttrade(trendMultiplier, reverseMultiplier)
        if doubleSided:
            longtrade(reverseMultiplier, trendMultiplier)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
