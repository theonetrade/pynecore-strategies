"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    barmerge, close, color, high, input, low, math, nz, open, plot,
    plotcandle, request, script, strategy, syminfo, ta, time, timestamp
)
from pynecore.types import Series


@script.strategy('MA Candles Supertrend Strategy', shorttitle='MACSTS', overlay=True, initial_capital=20000, default_qty_type=strategy.percent_of_equity, default_qty_value=100, commission_type=strategy.commission.percent, pyramiding=1, commission_value=0.01, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    MAType=input.string(title='Moving Average Type', defval='rma', options=('ema', 'sma', 'hma', 'rma', 'vwma', 'wma')),
    LoopbackBars=input.int(20, step=10),
    AtrMAType=input.string(title='Moving Average Type', defval='rma', options=('ema', 'sma', 'hma', 'rma', 'vwma', 'wma')),
    AtrLength=input.int(30, step=10),
    AtrMult=input(1),
    wicks=input(True),
    dThreshold=input.float(0.2, step=0.1, maxval=1),
    rThreshold=input.float(0.7, step=0.1, maxval=1),
    tradeDirection=input.string(title='Trade Direction', defval=strategy.direction.long, options=(strategy.direction.all, strategy.direction.long, strategy.direction.short)),
    i_startTime=input.time(defval=timestamp('01 Jan 2010 00:00 +0000'), title='Start Time'),
    i_endTime=input.time(defval=timestamp('01 Jan 2099 00:00 +0000'), title='End Time')
):
    adoptiveWicks: bool = False
    inDateRange = time >= i_startTime and time <= i_endTime
    strategy.risk.allow_entry_in(tradeDirection)
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

    def f_secureSecurity(_symbol, _res, _src: Series, _offset):
        return request.security(_symbol, _res, _src[_offset], lookahead=barmerge.lookahead_on)

    def f_getYearlyHighLowCondition():
        yhighrange = f_secureSecurity(syminfo.tickerid, '12M', high, 1)
        ylowrange = f_secureSecurity(syminfo.tickerid, '12M', low, 1)
        yearlyHighCondition = close > yhighrange * (1 - dThreshold) or close > ylowrange * (1 + rThreshold)
        yearlyLowCondition = close < ylowrange * (1 + dThreshold) or close < yhighrange * (1 - rThreshold)
        return (yearlyHighCondition, yearlyLowCondition)

    def f_getSupertrend(oOpen, oClose: Series, oHigh: Series, oLow: Series, AtrMAType, AtrLength, AtrMult, wicks):
        truerange = math.max(oHigh, oClose[1]) - math.min(oLow, oClose[1])
        averagetruerange = f_getMovingAverage(truerange, AtrMAType, AtrLength)
        atr = averagetruerange * AtrMult
        longWicks = adoptiveWicks and close < oClose or wicks
        shortWicks: Series = adoptiveWicks and close > oClose or wicks
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

    oOpen = f_getMovingAverage(open, MAType, LoopbackBars)
    oClose: Series = f_getMovingAverage(close, MAType, LoopbackBars)
    oHigh = f_getMovingAverage(high, MAType, LoopbackBars)
    oLow = f_getMovingAverage(low, MAType, LoopbackBars)
    colorByPreviousClose: bool = False
    candleColor = (color.green if oClose[1] < oClose else color.red if oClose[1] > oClose else color.silver) if colorByPreviousClose else color.green if oOpen < oClose else color.red if oOpen > oClose else color.silver
    plotcandle(oOpen, oHigh, oLow, oClose, 'Oscilator Candles', color=candleColor)
    yearlyHighCondition, yearlyLowCondition = f_getYearlyHighLowCondition()
    dir: Series
    dir, longStop, shortStop = f_getSupertrend(oOpen, oClose, oHigh, oLow, AtrMAType, AtrLength, AtrMult, wicks)
    trailingStop = longStop if dir == 1 else shortStop
    trendColor = color.green if dir == 1 else color.red
    plot(trailingStop, title='TrailingStop', color=trendColor, linewidth=2, style=plot.style_linebr)
    exitLongCondition = dir == -1 and (dir[1] == -1 and close < close[1] or close < longStop)
    exitShortCondition = dir == 1 and (dir[1] == 1 and close > close[1] or close > shortStop)
    longCondition = exitShortCondition and yearlyHighCondition and inDateRange
    shortCondition = exitLongCondition and yearlyLowCondition and inDateRange
    strategy.risk.allow_entry_in(tradeDirection)
    if longCondition:
        strategy.entry('Long', strategy.long, oca_name='oca_buy', oca_type=strategy.oca.cancel)
    if exitLongCondition:
        strategy.close('Long')
    if shortCondition:
        strategy.entry('Short', strategy.short, oca_name='oca_sell', oca_type=strategy.oca.cancel)
    if exitShortCondition:
        strategy.close('Short')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
