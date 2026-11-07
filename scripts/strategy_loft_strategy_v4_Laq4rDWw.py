"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bar_index, close, color, currency, high, input, label, math, nz, plot,
    script, strategy, string, time, timestamp
)
from pynecore.types import Persistent, PersistentSeries, Series


@script.strategy(title='Loft Strategy V4', overlay=True, pyramiding=0, default_qty_type=strategy.cash, default_qty_value=100, initial_capital=10000, currency=currency.USD, commission_value=0.05, commission_type=strategy.commission.percent, process_orders_on_close=True, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    gain=input.float(title='Kalman Gain:', defval=100.0, minval=1, maxval=10000.0, step=1),
    src: Series[float] = input(defval=close, title='Source:'),
    stopPercentBase=input.float(title='Beginning Approach(%)', defval=5.0, minval=0.1, maxval=30.0, step=0.1),
    stopPercentMin=input.float(title='Final Approach(%)', defval=1.0, minval=0.1, maxval=30.0, step=0.1),
    downStep=input.float(title='Approach Decrease Step', defval=0.001, minval=0.0, maxval=5, step=0.001),
    baseOrderQty=input.float(title='Base Order Quantity', defval=100.0, minval=0.001),
    maxOrderCount=input.int(title='Max Safe Order Attemp', defval=4, minval=1),
    priceDeviation=input.float(title='Safe Order Deviation', defval=3, minval=1.0, step=0.1),
    profitDeviation=input.float(title='Profit Deviation', defval=1.0, minval=1.0, maxval=10, step=0.1),
    maxTakeProfit=input.float(title='Max Take Profit(%)', defval=25.0, maxval=100, step=0.1),
    maxOrderQty=input.float(title='Max Order Quantity', defval=10000.0, minval=0.01),
    baseTP1=input.float(title='TP1(%)', defval=1.0, minval=0.0, maxval=100.0, step=0.1, inline='0'),
    qt1=input.int(title='QT1(%):', defval=40, minval=1, maxval=100, step=5, inline='0'),
    baseTP2=input.float(title='TP2(%)', defval=3.0, minval=0.0, maxval=100.0, step=0.1, inline='1'),
    qt2=input.int(title='QT2(%):', defval=30, minval=1, maxval=100, step=5, inline='1'),
    baseTP3=input.float(title='TP3(%)', defval=5.0, minval=0.0, maxval=100.0, step=0.1, inline='2'),
    qt3=input.int(title='QT3(%):', defval=30, minval=1, maxval=100, step=5, inline='2'),
    initialStopLoss=input.float(title='Stop Loss(%)', defval=0.0, minval=0.0, maxval=100.0, step=0.1),
    longEntry=input.bool(defval=True, title='Long Entry', inline='3'),
    shortEntry=input.bool(defval=True, title='Short Entry', inline='3'),
    useSafeStop2=input.bool(defval=True, title='Safe Stop After TP2', inline='6'),
    useSafeStop1=input.bool(defval=False, title='Safe Stop After TP1', inline='6'),
    fromDay=input.int(defval=1, title='From Date:', minval=1, maxval=31, inline='4'),
    fromMonth=input.int(defval=1, title='/', minval=1, maxval=12, inline='4'),
    fromYear=input.int(defval=2021, title='/', minval=2010, inline='4'),
    toDay=input.int(defval=30, title='To__ Date:', minval=1, maxval=31, inline='5'),
    toMonth=input.int(defval=12, title='/', minval=1, maxval=12, inline='5'),
    toYear=input.int(defval=2022, title='/', minval=2010, inline='5')
):
    start = timestamp(fromYear, fromMonth, fromDay, 0, 0)
    finish = timestamp(toYear, toMonth, toDay, 23, 59)
    def window():
        return True if time >= start and time <= finish else False

    enterLongComment: str = ''
    exitLongComment: str = ''
    enterShortComment: str = ''
    exitShortComment: str = ''
    longTPSL: str = ''
    longTP: str = ''
    longSL: str = ''
    shortTPSL: str = ''
    shortTP: str = ''
    shortSL: str = ''
    long: PersistentSeries[bool] = True
    stoppedOutLong: Persistent[bool] = False
    stoppedOutShort: Persistent[bool] = False
    kf: PersistentSeries[float] = 0.0
    velo: PersistentSeries[float] = 0.0
    orderQty: Persistent[float] = baseOrderQty
    stopLoss: Persistent[float] = initialStopLoss
    isProfit: Persistent[bool] = False
    barindex: Persistent[int] = 1
    winCounter: Persistent[int] = 0
    winCounterBuffer: Persistent[int] = 0
    failCounter: Persistent[int] = 0
    tp1: Persistent[float] = baseTP1
    tp2: Persistent[float] = baseTP2
    tp3: Persistent[float] = baseTP3
    isTakeTP1: Persistent[bool] = False
    isTakeTP2: Persistent[bool] = False
    isTakeTP3: Persistent[bool] = False
    isLastProfit: Persistent[bool] = True
    stopPercentMax: Persistent[float] = stopPercentBase
    stopPercent: Persistent[float] = stopPercentBase
    stopLine: PersistentSeries[float] = 0.0
    labelColor: Persistent = color.blue
    dk = src - nz(kf[1], src)
    smooth = nz(kf[1], src) + dk * math.sqrt(gain / 10000 * 2)
    velo = nz(velo[1], 0) + gain / 10000 * dk
    kf = smooth + velo
    if long == True:
        stopLine = kf - kf * (stopPercent / 100)
        if long[1] == True and stopLine <= stopLine[1]:
            stopLine = stopLine[1]
        elif long[1] == True:
            stopPercent = stopPercent - downStep
            if stopPercent < stopPercentMin:
                stopPercent = stopPercentMin
        if kf < stopLine:
            long = False
            stopPercent = stopPercentMax
            stopLine = kf + kf * (stopPercent / 100)
    else:
        stopLine = kf + kf * (stopPercent / 100)
        if long[1] == False and stopLine >= stopLine[1]:
            stopLine = stopLine[1]
        elif long[1] == False:
            stopPercent = stopPercent - downStep
            if stopPercent < stopPercentMin:
                stopPercent = stopPercentMin
        if kf > stopLine:
            long = True
            stopPercent = stopPercentMax
            stopLine = kf - kf * (stopPercent / 100)
    buySignall = window() and long and (not stoppedOutLong)
    sellSignall = window() and (not long) and (not stoppedOutShort)
    if longEntry and shortEntry:
        if buySignall and baseTP1 <= 0.0:
            if strategy.position_size < 0:
                if close < strategy.position_avg_price:
                    isLastProfit = True
            elif strategy.position_size == 0:
                if strategy.wintrades > winCounter:
                    isLastProfit = True
            else:
                isLastProfit = False
        elif sellSignall and baseTP1 <= 0.0:
            if strategy.position_size > 0:
                if close > strategy.position_avg_price:
                    isLastProfit = True
            elif strategy.position_size == 0:
                if strategy.wintrades > winCounter:
                    isLastProfit = True
            else:
                isLastProfit = False
        elif isTakeTP2 == True:
            isLastProfit = True
        else:
            isLastProfit = False
    elif longEntry:
        if sellSignall:
            winCounterBuffer = winCounter
        if buySignall:
            if winCounter > winCounterBuffer:
                isLastProfit = True
            else:
                isLastProfit = False
    elif shortEntry:
        if buySignall:
            winCounterBuffer = winCounter
        if sellSignall:
            if winCounter > winCounterBuffer:
                isLastProfit = True
            else:
                isLastProfit = False
    maxOrderSize: Persistent[float] = baseOrderQty * math.pow(priceDeviation, maxOrderCount - 1)
    if buySignall or sellSignall:
        if isLastProfit == False:
            orderQty = orderQty * priceDeviation
            tp1 = tp1 * profitDeviation
            tp2 = tp2 * profitDeviation
            tp3 = tp3 * profitDeviation
            tp1 = math.min(tp1, maxTakeProfit)
            tp2 = math.min(tp2, maxTakeProfit)
            tp3 = math.min(tp3, maxTakeProfit)
            if orderQty > maxOrderSize:
                failCounter = failCounter + 1
                orderQty = baseOrderQty
                tp1 = baseTP1
                tp2 = baseTP2
                tp3 = baseTP3
        else:
            orderQty = baseOrderQty
            tp1 = baseTP1
            tp2 = baseTP2
            tp3 = baseTP3
    if orderQty == maxOrderSize:
        labelColor = color.red
    else:
        labelColor = color.lime if isLastProfit else color.yellow
    if longEntry and shortEntry:
        if buySignall or sellSignall:
            label.new(x=bar_index, y=high, text='Qty:' + string.tostring(math.min(orderQty, maxOrderQty)) + ' | Worst Case:' + string.tostring(failCounter), color=labelColor)
    elif longEntry:
        if buySignall:
            label.new(x=bar_index, y=high, text='Qty:' + string.tostring(math.min(orderQty, maxOrderQty)) + ' | Worst Case:' + string.tostring(failCounter), color=labelColor)
    elif shortEntry:
        if sellSignall:
            label.new(x=bar_index, y=high, text='Qty:' + string.tostring(math.min(orderQty, maxOrderQty)) + ' | Worst Case:' + string.tostring(failCounter), color=labelColor)
    nz(orderQty, baseOrderQty)
    if longEntry and shortEntry:
        if long:
            if buySignall:
                strategy.close_all(comment=exitShortComment)
            if buySignall:
                strategy.entry('LONG', strategy.long, qty=math.min(orderQty, maxOrderQty), comment=enterLongComment)
            stoppedOutLong = True
            stoppedOutShort = False
        else:
            if sellSignall:
                strategy.close_all(comment=exitLongComment)
            if sellSignall:
                strategy.entry('SHORT', strategy.short, qty=math.min(orderQty, maxOrderQty), comment=enterShortComment)
            stoppedOutLong = False
            stoppedOutShort = True
    elif longEntry:
        if buySignall:
            strategy.entry('LONG', strategy.long, qty=math.min(orderQty, maxOrderQty), comment=enterLongComment)
        if sellSignall:
            strategy.close('LONG', comment=exitLongComment)
        if long:
            stoppedOutLong = True
            stoppedOutShort = False
        else:
            stoppedOutLong = False
            stoppedOutShort = True
    elif shortEntry:
        if sellSignall:
            strategy.entry('SHORT', strategy.short, qty=math.min(orderQty, maxOrderQty), comment=enterShortComment)
        if buySignall:
            strategy.close('SHORT', comment=exitShortComment)
        if not long:
            stoppedOutShort = True
            stoppedOutLong = False
        else:
            stoppedOutShort = False
            stoppedOutLong = True
    longProfitPrice1 = strategy.position_avg_price * (1 + tp1 * 0.01)
    longProfitPrice2 = strategy.position_avg_price * (1 + tp2 * 0.01)
    longProfitPrice3 = strategy.position_avg_price * (1 + tp3 * 0.01)
    shortProfitPrice1 = strategy.position_avg_price * (1 - tp1 * 0.01)
    shortProfitPrice2 = strategy.position_avg_price * (1 - tp2 * 0.01)
    shortProfitPrice3 = strategy.position_avg_price * (1 - tp3 * 0.01)
    longStopPrice = strategy.position_avg_price * (1 - stopLoss * 0.01)
    shortStopPrice = strategy.position_avg_price * (1 + stopLoss * 0.01)
    shortSafeStopPrice2 = strategy.position_avg_price * (1 - 0.2 * 0.01)
    longSafeStopPrice2 = strategy.position_avg_price * (1 + 0.2 * 0.01)
    longSafeStopPrice1 = stopLine
    shortSafeStopPrice1 = stopLine
    takeQty1 = math.min(orderQty, maxOrderQty) * qt1 / 100
    takeQty2 = math.min(orderQty, maxOrderQty) * qt2 / 100
    takeQty3 = math.min(orderQty, maxOrderQty) * qt3 / 100
    if strategy.position_size > 0:
        if close > longProfitPrice1 and tp1 > 0 and (isTakeTP1 == False):
            strategy.close(id='LONG', qty=takeQty1, comment='longTP 1')
            isTakeTP1 = True
        if close > longProfitPrice2 and tp2 > 0 and (isTakeTP2 == False):
            strategy.close(id='LONG', qty=takeQty2, comment='longTP 2')
            isTakeTP2 = True
        if close > longProfitPrice3 and tp3 > 0 and (isTakeTP3 == False):
            strategy.close(id='LONG', qty=takeQty3, comment='longTP 3')
            isTakeTP3 = True
        if isTakeTP2 == True and useSafeStop2:
            strategy.exit(id='LONG', stop=longSafeStopPrice2, comment='Long Safe Stop2')
        if isTakeTP1 == True and useSafeStop1:
            strategy.exit(id='LONG', stop=longSafeStopPrice1, comment='Long Safe Stop1')
    if strategy.position_size < 0:
        if close < shortProfitPrice1 and tp1 > 0 and (isTakeTP1 == False):
            strategy.close(id='SHORT', qty=takeQty1, comment='Short TP 1')
            isTakeTP1 = True
        if close < shortProfitPrice2 and tp2 > 0 and (isTakeTP2 == False):
            strategy.close(id='SHORT', qty=takeQty2, comment='Short TP 2')
            isTakeTP2 = True
        if close < shortProfitPrice3 and tp3 > 0 and (isTakeTP3 == False):
            strategy.close(id='SHORT', qty=takeQty3, comment='Short TP 3')
            isTakeTP3 = True
        if isTakeTP2 == True and useSafeStop2:
            strategy.exit(id='SHORT', stop=shortSafeStopPrice2, comment='Short Safe Stop2')
        if isTakeTP1 == True and useSafeStop1:
            strategy.exit(id='SHORT', stop=shortSafeStopPrice1, comment='Short Safe Stop1')
    if initialStopLoss > 0.0:
        if strategy.position_size > 0:
            strategy.exit(id='LONG', stop=longStopPrice, comment='Long Stop Loss')
        elif strategy.position_size < 0:
            strategy.exit(id='SHORT', stop=shortStopPrice, comment='Short Stop Loss')
    if buySignall or sellSignall:
        isTakeTP1 = False
        isTakeTP2 = False
        isTakeTP3 = False
        winCounter = strategy.wintrades
    lineColor1 = color.green if long else color.red
    lineColor2 = color.aqua if long else color.fuchsia
    kalmanPlot = plot(kf, color=lineColor1, linewidth=3, title='Kalman Filter')
    stopPlot = plot(stopLine, color=lineColor2, linewidth=2, title='Stop Loss Line')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
