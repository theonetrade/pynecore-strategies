"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, close, color, high, input, low, na, plot, script,
    strategy, ta, time, timestamp, volume
)
from pynecore.types import Series


@script.strategy('ADX | DMI Trend', overlay=True, initial_capital=10000, currency='USD', default_qty_type=strategy.percent_of_equity, default_qty_value=100, commission_type=strategy.commission.percent, commission_value=0.04, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    From_Year=input(defval=2019, title='From Year'),
    From_Month=input.int(defval=1, title='From Month', minval=1, maxval=12),
    From_Day=input.int(defval=1, title='From Day', minval=1, maxval=31),
    To_Year=input(defval=9999, title='To Year'),
    To_Month=input.int(defval=1, title='To Month', minval=1, maxval=12),
    To_Day=input.int(defval=1, title='To Day', minval=1, maxval=31),
    shortTrades=input(title='Allow short trades?', defval=True),
    adxlen=input(14, title='ADX Smoothing'),
    dilen=input(14, title='DI Period'),
    keyLevel=input(23, title='Keylevel for ADX'),
    adxLookbackEntry=input(3, title='Lookback Period for Slope (Entry)'),
    adxLookbackExit=input(1, title='Lookback Period for Slope (Exit)'),
    volFilter=input(title='Use Volume as Entry Filter?', defval=True),
    volType=input.string(defval='Multiplier * Average', options=('Multiplier * Average', 'Manual', 'Multiplier * Average AND Manual'), title='Volume Filtering Method'),
    volMult=input.float(title='Volume Trigger Multiplier', defval=2, step=0.1),
    volSMA=input.int(title='Volume Trigger Average Bars Back', defval=20, step=1),
    volManual=input.int(20000, title='Manual Volume Value', step=1000),
    useMaFilter=input(title='Use MA for Entry Filtering?', defval=True),
    maType=input.string(defval='EMA', options=('EMA', 'SMA'), title='MA Type For Filtering'),
    maLength=input.int(defval=200, title='MA Period for Filtering', minval=1),
    useATR=input(title='Use ATR for Trailing Stop?', defval=True),
    atrLookback=input(defval=14, title='ATR Lookback Period'),
    multiplier=input.float(defval=2, title='ATR Multiplier', step=0.1, minval=0.5, maxval=4),
    trigInput=input.string(title='Execute Trades On...', defval='Wick', options=('Wick', 'Close')),
    showInput=input.string(title='Show Trailing ATR', defval='Both', options=('Support', 'Resistance', 'Both')),
    useSAR=input(title='Use SAR for Trailing Stop?', defval=True),
    sarStart=input(0.02, 'Start'),
    sarIncrement=input(0.02, 'Increment'),
    sarMaximum=input(0.2, 'Max Value')
):
    Start = timestamp(From_Year, From_Month, From_Day, 0, 0)
    Finish = timestamp(To_Year, To_Month, To_Day, 23, 59)
    xVol = ta.sma(volume, volSMA)
    xVolMult = xVol * volMult
    manualCompare = volManual > xVolMult
    xVolManual = volManual if manualCompare == True else xVolMult
    volCheck = xVolMult if volFilter == True and volType == 'Multiplier * Average' else volManual if volFilter == True and volType == 'Manual' else xVolManual if volFilter == True and volType == 'Multiplier * Average AND Manual' else 0
    def ma(maType, src, length):
        return ta.ema(src, length) if maType == 'EMA' else ta.sma(src, length)

    maFilter = ma(maType, close, maLength)
    plot(maFilter, title='Trend Filter MA', color=color.new(color.green, 50), linewidth=3, style=plot.style_line)
    __block_result__ = na
    if useMaFilter == True:
        __block_result__ = maFilter
    else:
        __block_result__ = close
    maFilterCheck = __block_result__
    atrValue = ta.atr(atrLookback)
    atrMultiplied = atrValue * multiplier
    atrLow = low - atrMultiplied
    atrHigh = high + atrMultiplied
    trailAtrLow: Series = atrLow
    trailAtrHigh: Series = atrHigh
    trailAtrLow = trailAtrLow if na(trailAtrLow[1]) else atrLow if atrLow >= trailAtrLow[1] else trailAtrLow[1]
    trailAtrHigh = trailAtrHigh if na(trailAtrHigh[1]) else atrHigh if atrHigh <= trailAtrHigh[1] else trailAtrHigh[1]
    trigResistance = close if trigInput == 'Close' else high if trigInput == 'Wick' else na
    trigSupport = close if trigInput == 'Close' else low if trigInput == 'Wick' else na
    atrResistanceHit = trigResistance >= trailAtrHigh and useATR == True
    atrSupportHit = trigSupport <= trailAtrLow and useATR == True
    trailAtrLow = atrLow if atrSupportHit else trailAtrLow
    trailAtrHigh = atrHigh if atrResistanceHit else trailAtrHigh
    plotLow = trailAtrLow if useATR == True and showInput == 'Support' else trailAtrLow if useATR == True and showInput == 'Both' else na
    plotHigh = trailAtrHigh if useATR == True and showInput == 'Resistance' else trailAtrHigh if useATR == True and showInput == 'Both' else na
    plot(plotLow, color=color.new(color.gray, 0), style=plot.style_linebr, linewidth=1)
    plot(plotHigh, color=color.new(color.gray, 0), style=plot.style_linebr, linewidth=1)
    sarOut = ta.sar(sarStart, sarIncrement, sarMaximum) if useSAR else na
    plot(sarOut, 'ParabolicSAR', style=plot.style_cross, color=color.new(color.new('#3A6CA8'), 0))
    sarResistanceHit = trigResistance >= sarOut and useSAR == True
    sarSupportHit = trigSupport <= sarOut and useSAR == True
    adx: Series
    diplus, diminus, adx = ta.dmi(dilen, adxlen)
    buySignal = adx - adx[adxLookbackEntry] > 0 and adx > keyLevel and (diplus > diminus) and (time > Start) and (time < Finish) and (close >= maFilterCheck) and (volume > volCheck)
    shortSignal = adx - adx[adxLookbackEntry] > 0 and adx > keyLevel and (diplus < diminus) and (time > Start) and (time < Finish) and (close <= maFilterCheck) and shortTrades and (volume > volCheck)
    sellSignal = adx - adx[adxLookbackExit] < 0 or atrSupportHit or sarSupportHit
    coverSignal = adx - adx[adxLookbackExit] < 0 or atrResistanceHit or sarResistanceHit
    if buySignal:
        strategy.entry('Long', strategy.long)
    if sellSignal:
        strategy.close('Long')
    if shortSignal:
        strategy.entry('Short', strategy.short)
    if coverSignal:
        strategy.close('Short')
    alertcondition(buySignal, title='ADX | DMI Long', message='ADX | DMI Long')
    alertcondition(shortSignal, title='ADX | DMI Short', message='ADX | DMI Short')
    alertcondition(sellSignal, title='ADX | DMI Sell', message='ADX | DMI Sell')
    alertcondition(coverSignal, title='ADX | DMI Cover', message='ADX | DMI Cover')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
