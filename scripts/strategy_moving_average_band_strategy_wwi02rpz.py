"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, bar_index, close, color, fill, format, high, input,
    label, location, low, na, plot, plotshape, script, shape, size, strategy, string, ta
)
from pynecore.types import Persistent


@script.strategy('Moving Average Band Strategy', shorttitle='MA Band strategy', overlay=True, default_qty_type=strategy.percent_of_equity, default_qty_value=100)
def main(
    maTypeInput=input.string('SMA', 'Moving Average Type', options=('SMA', 'EMA', 'WMA', 'HMA', 'VWMA', 'RMA')),
    maLength=input.int(40, 'MA Length', minval=1),
    __input_2__=input.float(0.0, 'Band Offset %', minval=0.0, step=0.1),
    longEnabled=input.bool(True, 'Enable Long Trades', group='Strategy Settings'),
    shortEnabled=input.bool(True, 'Enable Short Trades', group='Strategy Settings'),
    useRiskReward=input.bool(True, 'Use Risk:Reward Target', group='Strategy Settings'),
    riskRewardRatio=input.float(3.0, 'Risk:Reward Ratio', minval=0.5, step=0.5, group='Strategy Settings')
):
    bandOffset = __input_2__ / 100

    def ma(source, length, maType):
        __block_result__ = na
        __switch__ = maType
        if __switch__ == 'SMA':
            __block_result__ = ta.sma(source, length)
        elif __switch__ == 'EMA':
            __block_result__ = ta.ema(source, length)
        elif __switch__ == 'WMA':
            __block_result__ = ta.wma(source, length)
        elif __switch__ == 'HMA':
            __block_result__ = ta.hma(source, length)
        elif __switch__ == 'VWMA':
            __block_result__ = ta.vwma(source, length)
        elif __switch__ == 'RMA':
            __block_result__ = ta.rma(source, length)
        else:
            __block_result__ = ta.sma(source, length)
        return __block_result__

    upperBand = ma(high, maLength, maTypeInput) * (1 + bandOffset)

    lowerBand = ma(low, maLength, maTypeInput) * (1 - bandOffset)

    middleLine = (upperBand + lowerBand) / 2

    priceAboveBand = close > upperBand
    priceBelowBand = close < lowerBand
    priceBetweenBand = not priceAboveBand and (not priceBelowBand)

    bandColor = color.new(color.green, 85) if priceAboveBand else color.new(color.red, 85) if priceBelowBand else color.new(color.yellow, 85)

    p1 = plot(upperBand, title='Upper Band', color=color.blue, linewidth=2)
    p2 = plot(lowerBand, title='Lower Band', color=color.blue, linewidth=2)

    fill(p1, p2, color=bandColor, title='Band Fill')

    plot(middleLine, title='Middle Line', color=color.gray, linewidth=1, style=plot.style_circles)

    longCondition = ta.crossover(close, upperBand) and longEnabled and (strategy.position_size <= 0)
    shortCondition = ta.crossunder(close, lowerBand) and shortEnabled and (strategy.position_size >= 0)

    longEntryPrice: Persistent[float] = na(float)
    shortEntryPrice: Persistent[float] = na(float)
    longStopLoss: Persistent[float] = na(float)
    shortStopLoss: Persistent[float] = na(float)
    longTakeProfit: Persistent[float] = na(float)
    shortTakeProfit: Persistent[float] = na(float)
    exitPrice: Persistent[float] = na(float)

    if longCondition:
        longEntryPrice = close
        longStopLoss = lowerBand
        riskPerTrade = longEntryPrice - longStopLoss
        longTakeProfit = longEntryPrice + riskPerTrade * riskRewardRatio if useRiskReward else na
        strategy.entry('Long', strategy.long)

        label.new(bar_index, longEntryPrice, text=string.tostring(longEntryPrice, format.mintick), style=label.style_none, textcolor=color.green, size=size.small)

    if shortCondition:
        shortEntryPrice = close
        shortStopLoss = upperBand
        riskPerTrade = shortStopLoss - shortEntryPrice
        shortTakeProfit = shortEntryPrice - riskPerTrade * riskRewardRatio if useRiskReward else na
        strategy.entry('Short', strategy.short)

        label.new(bar_index, shortEntryPrice, text=string.tostring(shortEntryPrice, format.mintick), style=label.style_none, textcolor=color.red, size=size.small)

    longSLHit = strategy.position_size > 0 and low <= longStopLoss
    longTPHit = useRiskReward and strategy.position_size > 0 and (not na(longTakeProfit)) and (high >= longTakeProfit)
    longCrossExit = not useRiskReward and strategy.position_size > 0 and ta.crossunder(close, lowerBand)

    shortSLHit = strategy.position_size < 0 and high >= shortStopLoss
    shortTPHit = useRiskReward and strategy.position_size < 0 and (not na(shortTakeProfit)) and (low <= shortTakeProfit)
    shortCrossExit = not useRiskReward and strategy.position_size < 0 and ta.crossover(close, upperBand)

    if longSLHit:
        exitPrice__00000032__ = longStopLoss
        strategy.close('Long', comment='SL Hit')
        label.new(bar_index, exitPrice__00000032__, text=string.tostring(exitPrice__00000032__, format.mintick), style=label.style_none, textcolor=color.red, size=size.small)

    if longTPHit:
        exitPrice__00000036__ = longTakeProfit
        strategy.close('Long', comment='TP Hit')
        label.new(bar_index, exitPrice__00000036__, text=string.tostring(exitPrice__00000036__, format.mintick), style=label.style_none, textcolor=color.green, size=size.small)

    if longCrossExit:
        exitPrice__0000003a__ = close
        strategy.close('Long', comment='Cross Exit')
        label.new(bar_index, exitPrice__0000003a__, text=string.tostring(exitPrice__0000003a__, format.mintick), style=label.style_none, textcolor=color.orange, size=size.small)

    if shortSLHit:
        exitPrice__0000003e__ = shortStopLoss
        strategy.close('Short', comment='SL Hit')
        label.new(bar_index, exitPrice__0000003e__, text=string.tostring(exitPrice__0000003e__, format.mintick), style=label.style_none, textcolor=color.red, size=size.small)

    if shortTPHit:
        exitPrice__00000042__ = shortTakeProfit
        strategy.close('Short', comment='TP Hit')
        label.new(bar_index, exitPrice__00000042__, text=string.tostring(exitPrice__00000042__, format.mintick), style=label.style_none, textcolor=color.green, size=size.small)

    if shortCrossExit:
        exitPrice__00000046__ = close
        strategy.close('Short', comment='Cross Exit')
        label.new(bar_index, exitPrice__00000046__, text=string.tostring(exitPrice__00000046__, format.mintick), style=label.style_none, textcolor=color.orange, size=size.small)

    if strategy.position_size[1] != 0 and strategy.position_size == 0:
        longStopLoss = na
        longTakeProfit = na
        shortStopLoss = na
        shortTakeProfit = na

    alertcondition(longCondition, title='Long Entry Signal', message='MA Band Strategy: LONG Entry - Price crossed above upper band')
    alertcondition(shortCondition, title='Short Entry Signal', message='MA Band Strategy: SHORT Entry - Price crossed below lower band')
    alertcondition(longSLHit, title='Long SL Hit', message='MA Band Strategy: Long STOP LOSS Hit')
    alertcondition(longTPHit, title='Long TP Hit', message='MA Band Strategy: Long TAKE PROFIT Hit')
    alertcondition(longCrossExit, title='Long Cross Exit', message='MA Band Strategy: Long EXIT - Crossed below lower band')
    alertcondition(shortSLHit, title='Short SL Hit', message='MA Band Strategy: Short STOP LOSS Hit')
    alertcondition(shortTPHit, title='Short TP Hit', message='MA Band Strategy: Short TAKE PROFIT Hit')
    alertcondition(shortCrossExit, title='Short Cross Exit', message='MA Band Strategy: Short EXIT - Crossed above upper band')

    alertcondition(longCondition or shortCondition or longSLHit or longTPHit or longCrossExit or shortSLHit or shortTPHit or shortCrossExit, title='Any Signal', message='{"strategy":"MA_Band","action":"{{strategy.order.action}}","price":"{{close}}","time":"{{timenow}}"}')

    plotshape(longCondition, title='Long Entry', location=location.belowbar, color=color.new(color.green, 0), style=shape.triangleup, size=size.small)
    plotshape(shortCondition, title='Short Entry', location=location.abovebar, color=color.new(color.red, 0), style=shape.triangledown, size=size.small)
    plotshape(longSLHit, title='Long SL', location=location.abovebar, color=color.new(color.red, 0), style=shape.xcross, size=size.small, text='SL')
    plotshape(longTPHit, title='Long TP', location=location.abovebar, color=color.new(color.green, 0), style=shape.xcross, size=size.small, text='TP')
    plotshape(longCrossExit, title='Long Cross Exit', location=location.abovebar, color=color.new(color.orange, 0), style=shape.xcross, size=size.small, text='X')
    plotshape(shortSLHit, title='Short SL', location=location.belowbar, color=color.new(color.red, 0), style=shape.xcross, size=size.small, text='SL')
    plotshape(shortTPHit, title='Short TP', location=location.belowbar, color=color.new(color.green, 0), style=shape.xcross, size=size.small, text='TP')
    plotshape(shortCrossExit, title='Short Cross Exit', location=location.belowbar, color=color.new(color.orange, 0), style=shape.xcross, size=size.small, text='X')

    plot(longStopLoss if strategy.position_size > 0 else na, title='Long SL', color=color.red, linewidth=2, style=plot.style_linebr)
    plot(longTakeProfit if strategy.position_size > 0 and useRiskReward else na, title='Long TP', color=color.green, linewidth=2, style=plot.style_linebr)
    plot(shortStopLoss if strategy.position_size < 0 else na, title='Short SL', color=color.red, linewidth=2, style=plot.style_linebr)
    plot(shortTakeProfit if strategy.position_size < 0 and useRiskReward else na, title='Short TP', color=color.green, linewidth=2, style=plot.style_linebr)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
