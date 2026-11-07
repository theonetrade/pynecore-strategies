"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, close, color, hl2, input, location, math, na, nz, plot,
    plotshape, script, shape, size, strategy, ta, time, timestamp
)
from pynecore.types import Series


@script.strategy('3x SuperTrend Strategy (Mel0nTek) V1', calc_on_every_tick=True, overlay=True, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    testStartYear=input(2020, 'Backtest Start Year'),
    testStartMonth=input(1, 'Backtest Start Month'),
    testStartDay=input(1, 'Backtest Start Day'),
    direction__global__=input.int(0, title='Strategy Direction', minval=-1, maxval=1),
    plInput=input.float(1.5, title='P/L Ratio', step=0.1, minval=0.1),
    EMAInputlength=input.int(200, 'EMA Length', step=100, minval=1),
    srsiInputSmoothK=input.int(3, 'K', minval=1),
    srsiInputSmoothD=input.int(3, 'D', minval=1),
    srsiInputLengthRSI=input.int(14, 'Stoch RSI Length', minval=1),
    srsiInputLengthStoch=input.int(14, 'Stochastic Length', minval=1),
    srsiInputSrc: Series[float] = input(close, title='Stoch RSI Source'),
    srsiInputThresh=input.int(20, title='Stoch RSI Entry Zone +/-', minval=1),
    stInputSrc: Series[float] = input(hl2, title='SuperTrend Source'),
    stSlowInputLength=input.int(12, 'Slow SuperTrend Length', minval=1),
    stSlowInputMult=input.int(3, 'Slow SuperTrend Multiplier', minval=1),
    stMedInputLength=input.int(11, 'Med SuperTrend Length', minval=1),
    stMedInputMult=input.int(2, 'Med SuperTrend Multiplier', minval=1),
    stFastInputLength=input.int(10, 'Fast SuperTrend Length', minval=1),
    stFastInputMult=input.int(1, 'Fast SuperTrend Multiplier', minval=1),
    stInputchangeATR=input(title='Alternate SuperTrend ATR Calculation?', defval=True),
    showPLTargets=input(True, title='Show Open Profit/Loss Targets?'),
    showBuySell=input(True, title='Show Buy/Sell Indicators?')
):
    testPeriodStart = timestamp(testStartYear, testStartMonth, testStartDay, 0, 0)
    timeCondition = time >= testPeriodStart
    strategy.risk.allow_entry_in(strategy.direction.all if direction__global__ == 0 else strategy.direction.short if direction__global__ < 0 else strategy.direction.long)
    def superTrend(period, src, mult, chgATR):
        stATRSmooth = ta.sma(ta.tr, period)
        stATR = ta.atr(period) if chgATR else stATRSmooth
        stUP: Series = src - mult * stATR
        stUP1 = nz(stUP[1], stUP)
        stUP = math.max(stUP, stUP1) if close[1] > stUP1 else stUP
        stDN: Series = src + mult * stATR
        stDN1 = nz(stDN[1], stDN)
        stDN = math.min(stDN, stDN1) if close[1] < stDN1 else stDN
        stTrend: Series[int] = 1
        stTrend = nz(stTrend[1], stTrend)
        stTrend = 1 if stTrend == -1 and close > stDN1 else -1 if stTrend == 1 and close < stUP1 else stTrend
        stBuySignal = stTrend == 1 and stTrend[1] == -1
        stSellSignal = stTrend == -1 and stTrend[1] == 1
        stChangeCond = stTrend != stTrend[1]
        return (stUP, stDN, stTrend, stBuySignal, stSellSignal, stChangeCond)

    def stochRSI(smoothK, smoothD, lengthRSI, lengthStoch, src):
        rsiVal = ta.rsi(src, lengthRSI)
        k = ta.sma(ta.stoch(rsiVal, rsiVal, rsiVal, lengthStoch), smoothK)
        d = ta.sma(k, smoothD)
        return (k, d)

    stSlowUP, stSlowDN, stSlowTrend, stSlowBuy, stSlowSell, stSlowChanged = superTrend(stSlowInputLength, stInputSrc, stSlowInputMult, stInputchangeATR)
    stMedUP, stMedDN, stMedTrend, stMedBuy, stMedSell, stMedChanged = superTrend(stMedInputLength, stInputSrc, stMedInputMult, stInputchangeATR)
    stFastUP, stFastDN, stFastTrend, stFastBuy, stFastSell, stFastChanged = superTrend(stFastInputLength, stInputSrc, stFastInputMult, stInputchangeATR)
    srsiK, srsiD = stochRSI(srsiInputSmoothK, srsiInputSmoothD, srsiInputLengthRSI, srsiInputLengthStoch, srsiInputSrc)
    emaVal = ta.ema(close, EMAInputlength)
    plot(emaVal, 'K', color=color.new(color.new('#0094FF'), 0))
    plot(stSlowUP if stSlowTrend == 1 else na, title='Slow Up Trend', style=plot.style_linebr, linewidth=2, color=color.new(color.green, 0))
    plotshape(stSlowUP if stSlowBuy else na, title='Slow UpTrend Begins', location=location.absolute, style=shape.triangleup, size=size.tiny, color=color.new(color.green, 0))
    plot(na if stSlowTrend == 1 else stSlowDN, title='Slow Down Trend', style=plot.style_linebr, linewidth=2, color=color.new(color.red, 0))
    plotshape(stSlowDN if stSlowSell else na, title='Slow DownTrend Begins', location=location.absolute, style=shape.triangledown, size=size.tiny, color=color.new(color.red, 0))
    plot(stMedUP if stMedTrend == 1 else na, title='Med Up Trend', style=plot.style_linebr, linewidth=2, color=color.new(color.green, 0))
    plotshape(stMedUP if stMedBuy else na, title='Med UpTrend Begins', location=location.absolute, style=shape.triangleup, size=size.tiny, color=color.new(color.green, 0))
    plot(na if stMedTrend == 1 else stMedDN, title='Med Down Trend', style=plot.style_linebr, linewidth=2, color=color.new(color.red, 0))
    plotshape(stMedDN if stMedSell else na, title='Med DownTrend Begins', location=location.absolute, style=shape.triangledown, size=size.tiny, color=color.new(color.red, 0))
    plot(stFastUP if stFastTrend == 1 else na, title='Fast Up Trend', style=plot.style_linebr, linewidth=2, color=color.new(color.green, 0))
    plotshape(stFastUP if stFastBuy else na, title='Fast UpTrend Begins', location=location.absolute, style=shape.triangleup, size=size.tiny, color=color.new(color.green, 0))
    plot(na if stFastTrend == 1 else stFastDN, title='Fast Down Trend', style=plot.style_linebr, linewidth=2, color=color.new(color.red, 0))
    plotshape(stFastDN if stFastSell else na, title='Fast DownTrend Begins', location=location.absolute, style=shape.triangledown, size=size.tiny, color=color.new(color.red, 0))
    longStop: Series[float] = na(float)
    longProfit: Series[float] = na(float)
    shortStop: Series[float] = na(float)
    shortProfit: Series[float] = na(float)
    emaTrend = 1 if emaVal < close else -1
    stCount: int = 0
    stCount = stFastTrend + stMedTrend + stSlowTrend
    crossover_1 = ta.crossover(srsiK, srsiD)
    stochLongCond = srsiK < srsiInputThresh and crossover_1
    stLongCond = stCount >= 1
    longCondition = emaTrend > 0 and stochLongCond and stLongCond
    tempStopLong = (stMedUP if stCount == 3 else stSlowUP) if longCondition else longStop
    longStopDelta = math.abs(close - tempStopLong)
    tempProfitLong = close + plInput * longStopDelta if longCondition else longProfit
    longStop = (tempStopLong if longCondition else na) if strategy.position_size <= 0 else longStop[1]
    longProfit = (tempProfitLong if longCondition else na) if strategy.position_size <= 0 else longProfit[1]
    crossunder_1 = ta.crossunder(srsiK, srsiD)
    stochShortCond = srsiK > 100 - srsiInputThresh and crossunder_1
    stShortCond = stCount <= -1
    shortCondition = emaTrend < 0 and stochShortCond and stShortCond
    tempStopShort = (stMedDN if stCount == -3 else stSlowDN) if shortCondition else shortStop
    shortStopDelta = math.abs(close - tempStopShort)
    tempProfitShort = close - plInput * shortStopDelta if shortCondition else shortProfit
    shortStop = (tempStopShort if shortCondition else na) if strategy.position_size >= 0 else shortStop[1]
    shortProfit = (tempProfitShort if shortCondition else na) if strategy.position_size >= 0 else shortProfit[1]
    strategy.exit('TP/SL', 'LongPos', stop=longStop, limit=longProfit)
    strategy.exit('TP/SL', 'ShortPos', stop=shortStop, limit=shortProfit)
    if longCondition and timeCondition:
        strategy.entry('LongPos', strategy.long, stop=longStop, oca_name='3xST', oca_type=strategy.oca.cancel, comment='Long')
    else:
        strategy.cancel(id='LongPos')
    if shortCondition and timeCondition:
        strategy.entry('ShortPos', strategy.short, stop=shortStop, oca_name='3xST', oca_type=strategy.oca.cancel, comment='Short')
    else:
        strategy.cancel(id='ShortPos')
    plot((na if strategy.position_size <= 0 else longStop) if showPLTargets else na, title='Long Stop Loss', color=color.new(color.new('#FF0000'), 0), style=plot.style_linebr, linewidth=2)
    plot((na if strategy.position_size <= 0 else longProfit) if showPLTargets else na, title='Long Profit Target', color=color.new(color.new('#00FF00'), 0), style=plot.style_linebr, linewidth=2)
    plot((na if strategy.position_size >= 0 else shortStop) if showPLTargets else na, title='Short Stop Loss', color=color.new(color.new('#FF0000'), 0), style=plot.style_linebr, linewidth=2)
    plot((na if strategy.position_size >= 0 else shortProfit) if showPLTargets else na, title='Short Profit Target', color=color.new(color.new('#00FF00'), 0), style=plot.style_linebr, linewidth=2)
    plotshape(1 if showBuySell and longCondition else na, title='Buy Arrow', location=location.belowbar, color=color.new(color.green, 0), style=shape.arrowup, text='BUY', textcolor=color.new(color.green, 0), size=size.small)
    plotshape(1 if showBuySell and shortCondition else na, title='Sell Arrow', location=location.abovebar, color=color.new(color.red, 0), style=shape.arrowdown, text='SELL', textcolor=color.new(color.red, 0), size=size.small)
    alertcondition(longCondition, title='3xST Buy alert', message='Buy')
    alertcondition(shortCondition, title='3xST SELL alert', message='Sell')
    alertcondition(stSlowChanged, title='3xST Slow Trend alert', message='Slow Trend Changed')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
