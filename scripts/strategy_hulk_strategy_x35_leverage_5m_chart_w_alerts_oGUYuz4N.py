"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alert, barmerge, close, color, fill, fixnan, high, input, low, math, na,
    plot, request, script, strategy, string, syminfo, ta
)
from pynecore.types import Series


@script.strategy('Hulk Scalper x35 Leverage', shorttitle='Smash Pullback Strat', overlay=True, initial_capital=100, default_qty_type=strategy.percent_of_equity, default_qty_value=100, margin_long=0, margin_short=0, close_by_id=True)
def main(
    rsiLength=input.int(20),
    RsiTopInput=input.int(2),
    RsiBotInput=input.int(-2),
    adxlen=input(14, title='ADX Smoothing'),
    dilen=input(14, title='DI Length'),
    ADXfilterlevel=input.int(33, title='ADX filter amount'),
    FastMacdLength=input.int(12, group='MACD'),
    SlowMacdLength=input.int(26, group='MACD'),
    SignalLength=input.int(11, group='MACD'),
    MacdTickAmountNeeded=input.float(5.45, title='Tick Amount for entry', group='MACD'),
    res=input.timeframe('1', group='MACD'),
    EmaFastLength=input.int(50, title='Ema Fast Length'),
    EmaSlowLength=input.int(200, title='Ema Slow Length'),
    StrongUpTrendCol=input.color(color.rgb(74, 255, 163)),
    StrongDownTrendCol=input.color(color.rgb(255, 71, 84)),
    MaxTrades_PerCross_Checkbox=input.bool(True, 'Limit Trades Per Cross', group='Filters'),
    MaxTrades=input.int(6),
    TakeProfitInput=input.float(0.0135, title='Take Profit %', group='TP/SL'),
    StopLossInput=input.float(0.011, title='Stop Loss %', group='TP/SL')
):
    rsi = ta.rsi(close, rsiLength)
    rsiWeighted = rsi - 50
    def dirmov(len):
        up = ta.change(high)
        down = -ta.change(low)
        plusDM = na if na(up) else up if up > down and up > 0 else 0
        minusDM = na if na(down) else down if down > up and down > 0 else 0
        truerange = ta.rma(ta.tr, len)
        plus = fixnan(100 * ta.rma(plusDM, len) / truerange)
        minus = fixnan(100 * ta.rma(minusDM, len) / truerange)
        return (plus, minus)

    def adx(dilen, adxlen):
        plus, minus = dirmov(dilen)
        sum = plus + minus
        adx__00000015__ = 100 * ta.rma(math.abs(plus - minus) / (1 if sum == 0 else sum), adxlen)
        return adx__00000015__

    sig = adx(dilen, adxlen)
    FastMacd, SlowMacd, Macdhist = ta.macd(close, FastMacdLength, SlowMacdLength, SignalLength)
    MACD = request.security(syminfo.tickerid, res, Macdhist, gaps=barmerge.gaps_on)
    MACDisAboveBand = MACD > MacdTickAmountNeeded
    MACDisBelowBand = MACD < MacdTickAmountNeeded * -1
    emaFast = ta.ema(close, EmaFastLength)
    emaSlow = ta.ema(close, EmaSlowLength)
    emaDist = emaFast - emaSlow
    EmaLengthFraction = emaDist / 4
    emafrac5 = emaSlow + EmaLengthFraction
    emafrac4 = emaSlow + EmaLengthFraction * 2
    emafrac3 = emaSlow + EmaLengthFraction * 3
    emafrac2 = emaSlow + EmaLengthFraction * 4
    UptrendCol_DowntrendCol = StrongUpTrendCol if emaFast >= emaSlow else StrongDownTrendCol
    ema1p = plot(emaFast, color=color.new(color.new('#000000'), transp=100))
    ema2p = plot(emafrac2, color=color.new(color.new('#000000'), transp=100))
    ema3p = plot(emafrac3, color=color.new(color.new('#000000'), transp=100))
    ema4p = plot(emafrac4, color=color.new(color.new('#000000'), transp=100))
    ema5p = plot(emafrac5, color=color.new(color.new('#000000'), transp=100))
    ema6p = plot(emaSlow, color=color.new(color.new('#000000'), transp=100))
    fill(ema2p, ema3p, color=color.new(UptrendCol_DowntrendCol, 70))
    fill(ema3p, ema4p, color=color.new(UptrendCol_DowntrendCol, 60))
    fill(ema4p, ema5p, color=color.new(UptrendCol_DowntrendCol, 50))
    fill(ema5p, ema6p, color=color.new(UptrendCol_DowntrendCol, 40))
    FastEma_above_SlowEma = emaFast > emaSlow
    FastEma_below_SlowEma = emaFast < emaSlow
    crossover_1 = ta.crossover(emaSlow, emaFast)
    emaCrossEvent = ta.crossover(emaFast, emaSlow) or crossover_1
    TrdCount: Series[int] = 0
    if TrdCount[1] > 0:
        TrdCount = TrdCount[1]
    crossover_2 = ta.crossover(emaSlow, emaFast)
    emaXevent = ta.crossover(emaFast, emaSlow) or crossover_2
    if emaXevent:
        TrdCount = 0
    IsMaxTrades_BelowCap = TrdCount[1] < MaxTrades
    if not MaxTrades_PerCross_Checkbox:
        IsMaxTrades_BelowCap = True
    Long_takeProfit = close * (1 + TakeProfitInput)
    Long_stopLoss = close * (1 - StopLossInput)
    Short_takeProfit = close * (1 - TakeProfitInput)
    Short_stopLoss = close * (1 + StopLossInput)
    LongConditionPt1 = close > emaSlow and MACDisBelowBand and (sig > ADXfilterlevel)
    LongConditionPt2 = FastEma_above_SlowEma and IsMaxTrades_BelowCap and (strategy.position_size == 0)
    LongConditionPt3 = rsiWeighted < RsiTopInput and rsiWeighted > RsiBotInput
    ShortConditionPt1 = close < emaSlow and MACDisAboveBand and (sig > ADXfilterlevel)
    ShortConditionPt2 = FastEma_below_SlowEma and IsMaxTrades_BelowCap and (strategy.position_size == 0)
    ShortConditionPt3 = rsiWeighted < RsiTopInput and rsiWeighted > RsiBotInput
    longCondition = LongConditionPt1 and LongConditionPt2 and LongConditionPt3
    if longCondition:
        strategy.entry('long', strategy.long)
        strategy.exit('exit', 'long', limit=Long_takeProfit, stop=Long_stopLoss)
        TrdCount = TrdCount + 1
        alert('Go Long with TP at' + string.tostring(Long_takeProfit) + 'and SL at' + string.tostring(Long_stopLoss), alert.freq_once_per_bar_close)
    shortCondition = ShortConditionPt1 and ShortConditionPt2 and ShortConditionPt3
    if shortCondition:
        strategy.entry('short', strategy.short)
        strategy.exit('exit', 'short', limit=Short_takeProfit, stop=Short_stopLoss)
        TrdCount = TrdCount + 1
        alert('Go Short with TP at' + string.tostring(Short_takeProfit) + 'and SL at' + string.tostring(Short_stopLoss), alert.freq_once_per_bar_close)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
