"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, fill, high, input, low, math, na, plot, script, strategy,
    ta, time, timestamp
)
from pynecore.types import Persistent


@script.strategy('Advanced Position Management [Mr_Rakun]', overlay=True, default_qty_type=strategy.cash, initial_capital=100000, default_qty_value=50000, margin_long=0, margin_short=0, close_by_id=True)
def main(
    fastLength=input(10, 'Fast MA Length', group='Strategy'),
    slowLength=input(20, 'Slow MA Length', group='Strategy'),
    posManagement=input.bool(True, '========== Advanced Position Management =========='),
    posType=input.string('Both', 'Strategy Type', options=('Both', 'Long', 'Short'), group='Strategy Type'),
    tp1Percent=input.float(2.0, 'Take Profit 1 %                                               ', minval=0.1, maxval=99, step=0.1, group='position management', inline='tp1'),
    tp1PositionPercent=input.int(30, 'Qty %', minval=1, maxval=100, step=1, group='position management', inline='tp1'),
    tp2Percent=input.float(4.0, 'Take Profit 2 %                                               ', minval=0.1, maxval=99, step=0.1, group='position management', inline='tp2'),
    tp2PositionPercent=input.int(30, 'Qty %', minval=1, maxval=100, step=1, group='position management', inline='tp2'),
    useTP2=input.bool(True, '', group='position management', inline='tp2'),
    tp3Percent=input.float(6.0, 'Take Profit 3 %                                               ', minval=0.1, maxval=99, step=0.1, group='position management', inline='tp3'),
    __input_10__=input.int(40, 'Qty %', minval=1, maxval=100, step=1, group='position management', inline='tp3'),
    useTP3=input.bool(True, '', group='position management', inline='tp3'),
    initialStopLossPercent=input.float(2.0, 'Initial Stop Loss %', minval=0.1, maxval=99, step=0.1, group='Stop Loss'),
    trailingStopType=input.string('Percent', 'Trailing Stop Type                                               ', options=('Percent', 'Previous TP'), group='Stop Loss', inline='stopuse'),
    useTrailingStop=input.bool(False, '', group='Stop Loss', inline='stopuse'),
    trailingStopPercent=input.float(3, 'Trailing Stop % (if Percent type)', minval=0.1, maxval=10, step=0.1, group='Stop Loss'),
    trailingStopActivationPercent=input.float(3.0, 'Trailing Stop Activation %', minval=0.1, maxval=10, step=0.1, group='Stop Loss'),
    limit_date_range=input.bool(title='Test Range', defval=True, group='Backtest'),
    start_time=input.time(defval=timestamp('11 OCT 2022 00:00 +0000'), title='Backtest Start', group='Backtest'),
    end_time=input.time(defval=timestamp('31 Dec 2080 00:00 +0000'), title='Backtest End', group='Backtest')
):
    fastMA = ta.ema(close, fastLength)
    slowMA = ta.ema(close, slowLength)
    plot(fastMA, color=color.blue, title='Fast MA')
    plot(slowMA, color=color.red, title='Slow MA')
    longCondition = ta.crossover(fastMA, slowMA)
    shortCondition = ta.crossunder(fastMA, slowMA)
    tp3PositionPercent = __input_10__ + 2
    in_date_range: bool = True
    if limit_date_range:
        in_date_range = time >= start_time and time <= end_time
    else:
        in_date_range = True
    entryPrice: Persistent[float] = na(float)
    currentStopLoss: Persistent[float] = na(float)
    tp1Price: Persistent[float] = na(float)
    tp2Price: Persistent[float] = na(float)
    tp3Price: Persistent[float] = na(float)
    trailingStopActive: Persistent[bool] = False
    highestSinceEntry: Persistent[float] = na(float)
    lowestSinceEntry: Persistent[float] = na(float)
    lastTPHit: Persistent[int] = 0
    def position_amount(ep: float, tp1: int, tp2: int, tp3: int):
        amount: Persistent[float] = strategy.default_entry_qty(ep)
        part1: Persistent[float] = math.round(amount * tp1 / 100, 3)
        part2: Persistent[float] = math.round(amount * tp2 / 100, 3)
        part3: Persistent[float] = math.round(amount * tp3 / 100, 3)
        total = part1 + part2 + part3
        return total

    def updateTrailingStopTP(currentPrice, isLong, currentStop, entry, tp1, tp2, tp3, lastHit):
        newStop = currentStop
        newLastHit = lastHit
        if isLong:
            if currentPrice >= tp3 and lastHit < 3:
                newStop = tp2
                newLastHit = 3
            elif currentPrice >= tp2 and lastHit < 2:
                newStop = tp1
                newLastHit = 2
            elif currentPrice >= tp1 and lastHit < 1:
                newStop = entry
                newLastHit = 1
        else:
            if currentPrice <= tp3 and lastHit < 3:
                newStop = tp2
                newLastHit = 3
            elif currentPrice <= tp2 and lastHit < 2:
                newStop = tp1
                newLastHit = 2
            elif currentPrice <= tp1 and lastHit < 1:
                newStop = entry
                newLastHit = 1
        return (newStop, newLastHit)

    if longCondition and (posType == 'Both' or posType == 'Long') and (strategy.position_size == 0 or strategy.position_size < 0) and in_date_range:
        entryPrice = close
        currentStopLoss = close * (1 - initialStopLossPercent / 100)
        tp1Price = close * (1 + tp1Percent / 100)
        tp2Price = close * (1 + tp2Percent / 100)
        tp3Price = close * (1 + tp3Percent / 100)
        trailingStopActive = False
        highestSinceEntry = close
        lastTPHit = 0
        longAmount = position_amount(entryPrice, tp1PositionPercent, tp1PositionPercent, tp1PositionPercent)
        strategy.entry('Long', strategy.long, qty=longAmount)
    if shortCondition and (posType == 'Both' or posType == 'Short') and (strategy.position_size == 0 or strategy.position_size > 0) and in_date_range:
        entryPrice = close
        currentStopLoss = close * (1 + initialStopLossPercent / 100)
        tp1Price = close * (1 - tp1Percent / 100)
        tp2Price = close * (1 - tp2Percent / 100)
        tp3Price = close * (1 - tp3Percent / 100)
        trailingStopActive = False
        lowestSinceEntry = close
        lastTPHit = 0
        shortAmount = position_amount(entryPrice, tp1PositionPercent, tp1PositionPercent, tp1PositionPercent)
        strategy.entry('Short', strategy.short, qty=shortAmount)
    if strategy.position_size != 0 and useTrailingStop:
        isLong = strategy.position_size > 0
        currentPrice = high if isLong else low
        profitPercent = (currentPrice - entryPrice) / entryPrice * 100 if isLong else (entryPrice - currentPrice) / entryPrice * 100
        if profitPercent >= trailingStopActivationPercent and (not trailingStopActive):
            trailingStopActive = True
        if trailingStopActive:
            if trailingStopType == 'Percent':
                newStopLoss = currentPrice * (1 - trailingStopPercent / 100) if isLong else currentPrice * (1 + trailingStopPercent / 100)
                currentStopLoss = math.max(currentStopLoss, newStopLoss) if isLong else math.min(currentStopLoss, newStopLoss)
            elif trailingStopType == 'Previous TP':
                newStop, newLastHit = updateTrailingStopTP(currentPrice, isLong, currentStopLoss, entryPrice, tp1Price, tp2Price, tp3Price, lastTPHit)
                currentStopLoss = newStop
                lastTPHit = newLastHit
    if strategy.position_size > 0:
        strategy.exit('TP1 Long', 'Long', qty_percent=tp1PositionPercent, limit=tp1Price)
        if useTP2:
            strategy.exit('TP2 Long', 'Long', qty_percent=tp2PositionPercent, limit=tp2Price)
        if useTP3:
            strategy.exit('TP3 Long', 'Long', qty_percent=tp3PositionPercent, limit=tp3Price)
    cross_1 = ta.cross(low, currentStopLoss)
    if strategy.position_size > 0 and cross_1:
        strategy.close('Long', 'SL Long')
    if strategy.position_size < 0:
        strategy.exit('TP1 Short', 'Short', qty_percent=tp1PositionPercent, limit=tp1Price)
        if useTP2:
            strategy.exit('TP2 Short', 'Short', qty_percent=tp2PositionPercent, limit=tp2Price)
        if useTP3:
            strategy.exit('TP3 Short', 'Short', qty_percent=tp3PositionPercent, limit=tp3Price)
    cross_2 = ta.cross(high, currentStopLoss)
    if strategy.position_size < 0 and cross_2:
        strategy.close('Short', 'SL Short')
    avg = plot(entryPrice if strategy.position_size != 0 else na, color=color.gray, style=plot.style_linebr, title='Stop Loss')
    sl = plot(currentStopLoss if strategy.position_size != 0 else na, color=color.red, style=plot.style_linebr, title='Stop Loss')
    t1 = plot(tp1Price if strategy.position_size != 0 else na, color=color.green, style=plot.style_linebr, title='Take Profit 1')
    t2 = plot(tp2Price if useTP2 and strategy.position_size != 0 else na, color=color.lime, style=plot.style_linebr, title='Take Profit 2')
    t3 = plot(tp3Price if useTP3 and strategy.position_size != 0 else na, color=color.teal, style=plot.style_linebr, title='Take Profit 3')
    fill(avg, sl, color=color.new(color.red, 90))
    fill(avg, t1, color=color.new(color.green, 90))
    fill(t1, t2, color=color.new(color.green, 80))
    fill(t2, t3, color=color.new(color.green, 70))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
