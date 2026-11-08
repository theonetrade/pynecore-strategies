"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    alertcondition, array, bar_index, barstate, close, color, display, high,
    input, label, line, location, low, math, na, open, plot, plotshape, position, script, shape,
    size, string, ta, table, yloc
)
from pynecore.types import Line, Persistent, Series, Table


@script.indicator('Buy Sell Signal', overlay=True)
def main(
    emaFastLen=input.int(5, 'Fast EMA', minval=1),
    emaSlowLen=input.int(13, 'Slow EMA', minval=1),
    atrLen=input.int(14, 'ATR Period', minval=1),
    atrMultSL=input.float(0.5, 'SL Multiplier (ATR)', minval=0.1, step=0.1),
    riskReward=input.float(3.0, 'Risk:Reward (R:R)', minval=1.0, step=0.5),
    confirmCandle=input.bool(True, 'Require candle confirmation'),
    showEmaFastLabel=input.bool(True, 'Show Fast EMA', group='EMAs'),
    emaFastColor=input.color(color.green, 'Fast EMA Color', group='EMAs'),
    showEmaSlowLabel=input.bool(True, 'Show Slow EMA', group='EMAs'),
    emaSlowColor=input.color(color.orange, 'Slow EMA Color', group='EMAs')
):
    emaFast = ta.ema(close, emaFastLen)
    emaSlow = ta.ema(close, emaSlowLen)
    atr = ta.atr(atrLen)

    bullTrend: Series = emaFast > emaSlow
    bearTrend = emaFast < emaSlow
    trendChange = bullTrend != bullTrend[1]

    buyCondition1 = bullTrend and trendChange and (close > open)
    sellCondition1 = bearTrend and trendChange and (close < open)
    buyCondition2 = bullTrend and trendChange
    sellCondition2 = bearTrend and trendChange

    buySignal = buyCondition1 if confirmCandle else buyCondition2
    sellSignal = sellCondition1 if confirmCandle else sellCondition2

    entryPrice: Persistent[float] = na(float)
    stopLoss: Persistent[float] = na(float)
    takeProfitFinal: Persistent[float] = na(float)
    inPosition: Persistent[bool] = False
    positionType: Persistent[str] = ''

    tpLevels: Persistent[list[float]] = array.new_float(0)
    tpHitFlags: Persistent[list[bool]] = array.new_bool(0)

    tpFinalHit: bool = False
    slHit: bool = False
    invalidated: bool = False

    if inPosition and positionType == 'LONG':
        if high >= takeProfitFinal:
            tpFinalHit = True
            inPosition = False
            positionType = ''
        elif low <= stopLoss:
            slHit = True
            inPosition = False
            positionType = ''

    if inPosition and positionType == 'SHORT':
        if low <= takeProfitFinal:
            tpFinalHit = True
            inPosition = False
            positionType = ''
        elif high >= stopLoss:
            slHit = True
            inPosition = False
            positionType = ''

    if inPosition and array.size(tpLevels) > 0:
        for i in pine_range(0, array.size(tpLevels) - 1):
            if not array.get(tpHitFlags, i):
                if positionType == 'LONG' and high >= array.get(tpLevels, i):
                    array.set(tpHitFlags, i, True)
                elif positionType == 'SHORT' and low <= array.get(tpLevels, i):
                    array.set(tpHitFlags, i, True)

    showBuySignal: bool = False
    showSellSignal: bool = False
    invalidatedType: Persistent[str] = ''

    if buySignal:
        if not inPosition or positionType != 'LONG':
            if inPosition and positionType == 'SHORT':
                invalidated = True
                invalidatedType = 'SELL'
                inPosition = False

            entryPrice = close
            stopLoss = low - atr * atrMultSL
            risk = entryPrice - stopLoss
            takeProfitFinal = entryPrice + risk * riskReward

            array.clear(tpLevels)
            array.clear(tpHitFlags)
            numTPs = math.floor(riskReward)
            for i in pine_range(1, numTPs - 1):
                array.push(tpLevels, entryPrice + risk * i)
                array.push(tpHitFlags, False)

            inPosition = True
            positionType = 'LONG'
            showBuySignal = True

    if sellSignal:
        if not inPosition or positionType != 'SHORT':
            if inPosition and positionType == 'LONG':
                invalidated = True
                invalidatedType = 'BUY'
                inPosition = False

            entryPrice = close
            stopLoss = high + atr * atrMultSL
            risk = stopLoss - entryPrice
            takeProfitFinal = entryPrice - risk * riskReward

            array.clear(tpLevels)
            array.clear(tpHitFlags)
            numTPs = math.floor(riskReward)
            for i in pine_range(1, numTPs - 1):
                array.push(tpLevels, entryPrice - risk * i)
                array.push(tpHitFlags, False)

            inPosition = True
            positionType = 'SHORT'
            showSellSignal = True

    plot(emaFast, title='Fast EMA', color=color.new(emaFastColor, 0), linewidth=1, display=display.all if showEmaFastLabel else display.none)
    plot(emaSlow, title='Slow EMA', color=color.new(emaSlowColor, 0), linewidth=1, display=display.all if showEmaSlowLabel else display.none)

    plotshape(showBuySignal, 'BUY Signal', shape.labelup, location.belowbar, color.new(color.lime, 0), text='BUY', textcolor=color.white, size=size.small)
    plotshape(showSellSignal, 'SELL Signal', shape.labeldown, location.abovebar, color.new(color.red, 0), text='SELL', textcolor=color.white, size=size.small)

    plotshape(tpFinalHit, 'FINAL TAKE PROFIT', shape.circle, location.abovebar, color.new(color.new('#00FF00'), 0), text='🎯 TP', textcolor=color.new('#00FF00'), size=size.small)

    plotshape(slHit, 'STOP LOSS', shape.xcross, location.belowbar, color.new(color.new('#FF0000'), 0), text='SL', textcolor=color.white, size=size.small)

    plotshape(invalidated and invalidatedType == 'BUY', 'INVALIDATED BUY', shape.diamond, location.abovebar, color.new(color.yellow, 0), text='INV BUY', textcolor=color.rgb(97, 100, 107), size=size.tiny)
    plotshape(invalidated and invalidatedType == 'SELL', 'INVALIDATED SELL', shape.diamond, location.abovebar, color.new(color.yellow, 0), text='INV SELL', textcolor=color.rgb(97, 100, 107), size=size.tiny)

    tpAlreadyMarked: Persistent[list[bool]] = array.new_bool(0)

    if showBuySignal or showSellSignal:
        array.clear(tpAlreadyMarked)
        numTPs = math.floor(riskReward)
        for i in pine_range(1, numTPs - 1):
            array.push(tpAlreadyMarked, False)

    if inPosition and array.size(tpHitFlags) > 0 and (array.size(tpAlreadyMarked) > 0):
        for i in pine_range(0, array.size(tpHitFlags) - 1):
            if array.get(tpHitFlags, i) and (not array.get(tpAlreadyMarked, i)):
                label.new(bar_index, high, 'TP' + string.tostring(i + 1), style=label.style_label_down, color=color.new(color.green, 50), textcolor=color.white, size=size.tiny, yloc=yloc.abovebar)
                array.set(tpAlreadyMarked, i, True)

    entryLine: Persistent[Line] = na(Line)
    slLine: Persistent[Line] = na(Line)
    tpLineFinal: Persistent[Line] = na(Line)
    tpIntermediateLines: Persistent[list[Line]] = array.new_line(0)

    if inPosition and positionType != '':
        if na(entryLine):
            entryLine = line.new(bar_index - 10, entryPrice, bar_index + 10, entryPrice, color=color.new(color.white, 0), width=1, style=line.style_dashed)
        else:
            line.set_xy1(entryLine, bar_index - 10, entryPrice)
            line.set_xy2(entryLine, bar_index + 10, entryPrice)

        if na(slLine):
            slLine = line.new(bar_index, stopLoss, bar_index + 1, stopLoss, color=color.new(color.red, 0), width=2)
        else:
            line.set_xy1(slLine, bar_index, stopLoss)
            line.set_xy2(slLine, bar_index + 1, stopLoss)

        if na(tpLineFinal):
            tpLineFinal = line.new(bar_index, takeProfitFinal, bar_index + 1, takeProfitFinal, color=color.new(color.green, 0), width=2)
        else:
            line.set_xy1(tpLineFinal, bar_index, takeProfitFinal)
            line.set_xy2(tpLineFinal, bar_index + 1, takeProfitFinal)

        if array.size(tpIntermediateLines) == 0 and array.size(tpLevels) > 0:
            for i in pine_range(0, array.size(tpLevels) - 1):
                tpLine = line.new(bar_index, array.get(tpLevels, i), bar_index + 1, array.get(tpLevels, i), color=color.new(color.green, 60), width=1, style=line.style_dotted)
                array.push(tpIntermediateLines, tpLine)
        elif array.size(tpIntermediateLines) > 0:
            for i in pine_range(0, array.size(tpIntermediateLines) - 1):
                line.set_xy1(array.get(tpIntermediateLines, i), bar_index, array.get(tpLevels, i))
                line.set_xy2(array.get(tpIntermediateLines, i), bar_index + 1, array.get(tpLevels, i))
    else:
        if not na(entryLine):
            line.delete(entryLine)
            entryLine = na
        if not na(slLine):
            line.delete(slLine)
            slLine = na
        if not na(tpLineFinal):
            line.delete(tpLineFinal)
            tpLineFinal = na
        if array.size(tpIntermediateLines) > 0:
            for i in pine_range(0, array.size(tpIntermediateLines) - 1):
                line.delete(array.get(tpIntermediateLines, i))
            array.clear(tpIntermediateLines)

    infoTable: Persistent[Table] = table.new(position.top_right, 2, 5, bgcolor=color.new(color.black, 85), border_width=1)

    if barstate.islast:
        table.cell(infoTable, 0, 0, 'Status:', text_color=color.white, text_size=size.small)
        table.cell(infoTable, 1, 0, positionType if inPosition else 'No Position', text_color=color.yellow if inPosition else color.gray, text_size=size.small)

        if inPosition:
            table.cell(infoTable, 0, 1, 'Entry:', text_color=color.white, text_size=size.small)
            table.cell(infoTable, 1, 1, string.tostring(entryPrice, '#.##'), text_color=color.white, text_size=size.small)

            table.cell(infoTable, 0, 2, 'Stop Loss:', text_color=color.white, text_size=size.small)
            table.cell(infoTable, 1, 2, string.tostring(stopLoss, '#.##'), text_color=color.red, text_size=size.small)

            table.cell(infoTable, 0, 3, 'Take Profit:', text_color=color.white, text_size=size.small)
            table.cell(infoTable, 1, 3, string.tostring(takeProfitFinal, '#.##'), text_color=color.green, text_size=size.small)

            riskVal = math.abs(entryPrice - stopLoss)
            rewardVal = math.abs(takeProfitFinal - entryPrice)
            currentRR = rewardVal / riskVal

            table.cell(infoTable, 0, 4, 'R:R:', text_color=color.white, text_size=size.small)
            table.cell(infoTable, 1, 4, string.tostring(currentRR, '#.##') + ':1', text_color=color.orange, text_size=size.small)

    alertcondition(showBuySignal, '🟢 BUY Signal', '📈 BUY on {{ticker}} | Price: {{close}}')
    alertcondition(showSellSignal, '🔴 SELL Signal', '📉 SELL on {{ticker}} | Price: {{close}}')
    alertcondition(tpFinalHit, '🎯 Final Take Profit', '✅ Final TP hit on {{ticker}} | Price: {{close}}')
    alertcondition(slHit, '❌ Stop Loss', '🛑 SL triggered on {{ticker}} | Price: {{close}}')
    alertcondition(invalidated, '⚠️ Entry Invalidated', '⚠️ Previous entry invalidated on {{ticker}} | New signal detected')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
