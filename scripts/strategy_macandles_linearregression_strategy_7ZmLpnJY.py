"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, high, input, low, math, na, nz, open, plot, script,
    strategy, ta, time, timestamp
)
from pynecore.types import Series


@script.strategy('MACandles-LinearRegression-Strategy', shorttitle='MALinReg - Strategy', overlay=False, initial_capital=100000, default_qty_type=strategy.percent_of_equity, default_qty_value=100, commission_type=strategy.commission.percent, pyramiding=1, commission_value=0.01, margin_long=0, margin_short=0, close_by_id=True)
def main(
    MAType=input.string(title='Moving Average Type (MA Candles)', defval='hma', options=('ema', 'sma', 'hma', 'rma', 'vwma', 'wma')),
    LoopbackBars=input.int(60, title='Length (MA Candles)', step=10),
    MMAType=input.string(title='Moving Average Type (Momentum)', defval='ema', options=('ema', 'sma', 'hma', 'rma', 'vwma', 'wma')),
    MLength=input.int(20, title='MA Length (Momentum)', step=10),
    lb=input.int(40, title='Look Back Period Percentile High/Low', step=10, minval=10, maxval=100),
    ph=input(0.85, title='Highest Percentile - 0.90=90%, 0.95=95%, 0.99=99%'),
    pl=input(1.01, title='Lowest Percentile - 1.10=90%, 1.05=95%, 1.01=99%'),
    mult=input.float(3.0, minval=1, maxval=5, title='Bollinger Band Standard Devaition Up'),
    aggressiveLong=input(True),
    longTrades=input(True),
    useVixFix=input(False),
    i_startTime=input.time(defval=timestamp('01 Jan 2010 00:00 +0000'), title='Start Time'),
    i_endTime=input.time(defval=timestamp('01 Jan 2099 00:00 +0000'), title='End Time')
):
    resolution: str = ''
    inDateRange = time >= i_startTime and time <= i_endTime
    def f_getMovingAverage(source, MAType, length):
        ma = ta.sma(source, length)
        if MAType == 'ema':
            ma = ta.ema(source, length)
        if MAType == 'hma':
            ma = ta.hma(source, length)
        if MAType == 'rma':
            ma = ta.rma(source, length)
        if MAType == 'vwma':
            ma = ta.vwma(source, length)
        if MAType == 'wma':
            ma = ta.wma(source, length)
        return ma

    def f_getMACandles(resolution, MAType, LoopbackBars):
        oOpen = f_getMovingAverage(open, MAType, LoopbackBars)
        oClose = f_getMovingAverage(close, MAType, LoopbackBars)
        oHigh = f_getMovingAverage(high, MAType, LoopbackBars)
        oLow = f_getMovingAverage(low, MAType, LoopbackBars)
        return (oOpen, oClose, oHigh, oLow)

    def f_getVixFixLinReg(oClose, oLow, MLength):
        wvf = (ta.highest(oClose, MLength) - oLow) / ta.highest(oClose, MLength) * 100
        sDev = mult * ta.stdev(wvf, MLength)
        midLine = ta.sma(wvf, MLength)
        lowerBand = midLine - sDev
        upperBand = midLine + sDev
        rangeHigh = ta.highest(wvf, lb) * ph
        rangeLow = ta.lowest(wvf, lb) * pl
        col = color.lime if wvf >= upperBand or wvf >= rangeHigh else color.gray
        val: Series = ta.linreg(wvf, MLength, 0)
        absVal = math.abs(val)
        linRegColor = (color.green if val > 0 else color.orange) if val > val[1] else color.lime if val > 0 else color.red
        vixFixState: Series = 1 if col == color.lime else 0
        vixFixState = math.max(vixFixState, nz(vixFixState[1], 0)) if strategy.position_size == 0 else vixFixState
        return (val, absVal, wvf, col, linRegColor, vixFixState)

    def f_getMACandlesLinReg(oClose, MMAType, MLength, mult, lb, ph, pl):
        ma = f_getMovingAverage(oClose, MMAType, MLength)
        maDiff = oClose - ma
        val: Series = ta.linreg(maDiff, MLength, 0)
        absVal = math.abs(val)
        iff_1 = color.green if val > nz(val[1]) else color.lime
        iff_2 = color.red if val < nz(val[1]) else color.orange
        linRegColor = iff_1 if val > 0 else iff_2
        sDev = mult * ta.stdev(maDiff, MLength)
        midLine = ta.sma(maDiff, MLength)
        lowerBand = midLine - sDev
        upperBand = midLine + sDev
        rangeHigh = ta.highest(maDiff, lb) * ph
        rangeLow = ta.lowest(maDiff, lb) * pl
        col = color.lime if maDiff >= upperBand or maDiff >= rangeHigh else color.orange if maDiff <= lowerBand or maDiff <= rangeLow else color.silver
        absMaDiff = math.abs(maDiff)
        return (val, absVal, maDiff, absMaDiff, col, linRegColor)

    def f_getSupertrend(resolution, oOpen, oClose: Series, oHigh: Series, oLow: Series, AtrMAType, AtrLength, AtrMult, wicks):
        truerange = math.max(oHigh, oClose[1]) - math.min(oLow, oClose[1])
        averagetruerange = f_getMovingAverage(truerange, AtrMAType, AtrLength)
        atr = averagetruerange * AtrMult
        longWicks = wicks
        shortWicks: Series = wicks
        longStop: Series = oClose - atr
        longStopPrev = nz(longStop[1], longStop)
        longStop = math.max(longStop, longStopPrev) if (oLow[1] if longWicks else oClose[1]) > longStopPrev else longStop
        shortStop: Series = oClose + atr
        shortStopPrev = nz(shortStop[1], shortStop)
        shortStop = math.min(shortStop, shortStopPrev) if (oHigh[1] if shortWicks else oClose[1]) < shortStopPrev else shortStop
        dir: Series[int] = 1
        dir = nz(dir[1], dir)
        dir = 1 if dir == -1 and (oHigh if longWicks else oClose) > shortStopPrev else -1 if dir == 1 and (oLow if shortWicks[1] else oClose) < longStopPrev else dir
        return (dir, longStop, shortStop)

    def f_getMACandlesAndSupertrend(MAType, LoopbackBars, AtrMult, wicks):
        oOpen = f_getMovingAverage(open, MAType, LoopbackBars)
        oClose = f_getMovingAverage(close, MAType, LoopbackBars)
        oHigh = f_getMovingAverage(high, MAType, LoopbackBars)
        oLow = f_getMovingAverage(low, MAType, LoopbackBars)
        dir, longStop, shortStop = f_getSupertrend(resolution, oOpen, oClose, oHigh, oLow, MAType, LoopbackBars, AtrMult, wicks)
        return dir

    oClose: Series
    oOpen, oClose, oHigh, oLow = f_getMACandles(resolution, MAType, LoopbackBars)
    dir = f_getMACandlesAndSupertrend('sma', 200, 1, False)
    colorByPreviousClose: bool = False
    candleColor = (color.green if oClose[1] < oClose else color.red if oClose[1] > oClose else color.silver) if colorByPreviousClose else color.green if oOpen < oClose else color.red if oOpen > oClose else color.silver
    vval, vabsVal, wvf, vcol, vlinRegColor, vixFixState = f_getVixFixLinReg(oClose, oLow, MLength)
    col: Series
    linRegColor: Series
    val, absVal, maDiff, absMaDiff, col, linRegColor = f_getMACandlesLinReg(oClose, MMAType, MLength, mult, lb, ph, pl)
    plot(na if useVixFix else absMaDiff, title='Momentum', style=plot.style_histogram, linewidth=4, color=col)
    plot(wvf if useVixFix else na, title='VIX Fix', style=plot.style_histogram, linewidth=4, color=vcol)
    plot(na if useVixFix else -absVal, title='Linear Regression (Momentum)', style=plot.style_histogram, linewidth=4, color=linRegColor)
    plot(-vabsVal if useVixFix else na, title='Linear Regression (VIX Fix)', style=plot.style_histogram, linewidth=4, color=vlinRegColor)
    exitColor = color.orange if longTrades else color.silver
    exitPreviousColor = color.silver if longTrades else color.lime
    longCondition = (vixFixState == 1 and vlinRegColor == color.lime if useVixFix else linRegColor == color.orange and linRegColor[1] == color.red or (linRegColor == color.green and linRegColor[1] != color.green and aggressiveLong)) and inDateRange and (dir > 0)
    exitLongCondition = col == exitColor and col[1] == exitColor and (col[2] == exitPreviousColor) and (linRegColor != color.green or not aggressiveLong)
    if longCondition:
        strategy.entry('Long', strategy.long, oca_name='oca_buy', oca_type=strategy.oca.cancel)
    if exitLongCondition:
        strategy.close('Long')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
