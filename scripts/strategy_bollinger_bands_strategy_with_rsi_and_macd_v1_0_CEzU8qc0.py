"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    array, close, color, currency, input, math, na, plot, script, strategy,
    string, ta, time
)
from pynecore.types import Persistent, Series


@script.strategy(title='BB-strategy', calc_on_every_tick=True, max_labels_count=500, max_bars_back=1000, overlay=True, pyramiding=5, default_qty_value=3, initial_capital=100000, currency=currency.EUR, margin_long=0, margin_short=0, default_qty_type=strategy.fixed, close_by_id=True, na_bool=True)
def main(
    bbSource: Series[float] = input(title='BB source', defval=close),
    smaLength=input(title='Bollinger Bands SMA length', defval=20),
    stdLength=input(title='Bollinger Bands StdDev length', defval=2),
    __input_3__=input.float(title='Trail Long Loss (%) (min: 0.0)', minval=0.0, step=0.1, defval=4.0),
    __input_4__=input.float(title='Trail Short Loss (%) (min: 0.0)', minval=0.0, step=0.1, defval=4.0),
    maxOrders=input.int(title='Maximum orders (min: 1, max: 3)', minval=1, maxval=3, defval=2),
    posSize=input.int(title='Position size (min: 1, max: 100)', minval=1, maxval=100, defval=2),
    rsiChosen=input(title='Use RSI', defval=False),
    rsiSource: Series[float] = input(title='RSI source', defval=close),
    rsiPeriod=input.int(title='RSI period', minval=1, maxval=1000, defval=14),
    rsiBuy=input.int(title='RSI value for buy', minval=1, maxval=99, defval=30),
    rsiSell=input.int(title='RSI value for sell', minval=1, maxval=99, defval=70),
    macdChosen=input(title='Use MACD', defval=False),
    macdVariation=input(title='Use MACD variation (Use MACD must be selected)', defval=False),
    macdSource: Series[float] = input(title='MACD source', defval=close),
    fastLen=input.int(title='MACD fast length', minval=1, maxval=1000, defval=12),
    slowLen=input.int(title='MACD slow length', minval=1, maxval=1000, defval=26),
    signLen=input.int(title='MACD signal length', minval=1, maxval=1000, defval=9),
    longMaxTpChosen=input(title='Use maximum TP long', defval=True),
    __input_19__=input.float(title='Maximum take profit long (%) (min: 0.5, max: 30.0)', minval=0.5, step=0.1, defval=3.0, maxval=30.0),
    shortMaxTpChosen=input(title='Use maximum TP short', defval=True),
    __input_21__=input.float(title='Maximum take profit short (%) (min: 0.5, max: 30.0)', minval=0.5, step=0.1, defval=3.0, maxval=30.0)
):
    longTrailPerc = __input_3__ * 0.01
    shortTrailPerc = __input_4__ * 0.01
    longMaxTp = __input_19__ * 0.01
    shortMaxTp = __input_21__ * 0.01
    rsiValue = ta.rsi(rsiSource, rsiPeriod)
    histLine: Series
    macdLine, signalLine, histLine = ta.macd(macdSource, fastLen, slowLen, signLen)
    plot(macdLine, color=color.new(color.red, 0))
    plot(signalLine, color=color.new(color.green, 0))
    plot(histLine, color=color.new(color.yellow, 0), style=plot.style_histogram)
    upper: Series
    lower: Series
    middle, upper, lower = ta.bb(bbSource, smaLength, stdLength)
    idsLong: Persistent[list[str]] = array.new_string(maxOrders, na)
    idsShort: Persistent[list[str]] = array.new_string(maxOrders, na)
    stopLong: Persistent[list[float]] = array.new_float(maxOrders, 0.0)
    stopShort: Persistent[list[float]] = array.new_float(maxOrders, 999999.0)
    longPartialClose: Persistent[list[bool]] = array.new_bool(maxOrders, False)
    shortPartialClose: Persistent[list[bool]] = array.new_bool(maxOrders, False)
    opTp: Persistent[list[float]] = array.new_float(maxOrders, 0.0)
    opTpShort: Persistent[list[float]] = array.new_float(maxOrders, 0.0)
    canBuyMacd: bool = True
    if macdVariation:
        canBuyMacd = histLine[2] < histLine[1] and histLine[1] < histLine
        if not macdChosen:
            canBuyMacd = True
    else:
        canBuyMacd = histLine[2] < 0 and histLine[1] >= 0 and (histLine >= 0)
        if not macdChosen:
            canBuyMacd = True
    canSellMacd: bool = True
    if macdVariation:
        canSellMacd = histLine[2] > histLine[1] and histLine[1] > histLine
        if not macdChosen:
            canSellMacd = True
    else:
        canSellMacd = histLine[2] > 0 and histLine[1] <= 0 and (histLine <= 0)
        if not macdChosen:
            canSellMacd = True
    canBuyRsi: bool = True
    if rsiChosen:
        if rsiValue > rsiBuy:
            canBuyRsi = False
    canSellRsi: bool = True
    if rsiChosen:
        if rsiValue < rsiSell:
            canSellRsi = False
    canBuy: bool = False
    index: int = na(int)
    for i in pine_range(0, maxOrders - 1, 1):
        val: str = array.get(idsLong, i)
        if na(val):
            canBuy = True
            index = i
    canSell: bool = False
    indexSell: int = na(int)
    for i in pine_range(0, maxOrders - 1, 1):
        val: str = array.get(idsShort, i)
        if na(val):
            canSell = True
            indexSell = i
    isLong: bool = close[2] < lower[2] and close[1] > close[2] and (close > close[1]) and canBuy and (close[3] > close[2]) and (close < middle) and canBuyRsi and canBuyMacd
    isShort: bool = close[2] > upper[2] and close[1] < close[2] and (close < close[1]) and canSell and (close[3] < close[2]) and (close > middle) and canSellRsi and canSellMacd
    longStopPrice: float = 0.0
    shortStopPrice: float = 0.0
    tp: float = 0.0
    id: str = ''
    if isLong:
        id = string.tostring(time)
        strategy.entry(id=id, direction=strategy.long, qty=posSize)
        array.set(idsLong, index, id)
        stopValue = close * (1 - longTrailPerc)
        longStopPrice = stopValue
        array.set(stopLong, index, longStopPrice)
        tp = close * (1 + longMaxTp)
        array.set(opTp, index, tp)
    for i in pine_range(0, maxOrders - 1, 1):
        stopValue = close * (1 - longTrailPerc)
        longStopPrice = math.max(stopValue, array.get(stopLong, i))
        array.set(stopLong, i, longStopPrice)
        if (longMaxTpChosen and array.get(opTp, i) <= close or close >= upper or close <= array.get(stopLong, i)) and (not na(array.get(idsLong, i))):
            id = array.get(idsLong, i)
            strategy.close(id=id, qty=posSize)
            array.set(idsLong, i, na)
            array.set(stopLong, i, 0.0)
            array.set(longPartialClose, i, False)
        if close > middle and (not na(array.get(idsLong, i))) and (not array.get(longPartialClose, i)):
            id = array.get(idsLong, i)
            x: str = array.get(idsLong, i)
            strategy.close(id=id, qty=posSize / 2)
            array.set(longPartialClose, i, True)
    if isShort:
        id = string.tostring(time)
        strategy.entry(id=id, direction=strategy.short, qty=posSize)
        array.set(idsShort, indexSell, id)
        stopValue = close * (1 + shortTrailPerc)
        shortStopPrice = stopValue
        array.set(stopShort, indexSell, shortStopPrice)
        tp = close * (1 - shortMaxTp)
        array.set(opTpShort, indexSell, tp)
    for i in pine_range(0, maxOrders - 1, 1):
        stopValue = close * (1 + shortTrailPerc)
        shortStopPrice = math.min(stopValue, array.get(stopShort, i))
        array.set(stopShort, i, shortStopPrice)
        if (shortMaxTpChosen and array.get(opTpShort, i) >= close or close <= lower or close >= array.get(stopShort, i)) and (not na(array.get(idsShort, i))):
            id = array.get(idsShort, i)
            strategy.close(id=id, qty=posSize)
            array.set(idsShort, i, na)
            array.set(stopShort, i, 999999.0)
            array.set(shortPartialClose, i, False)
        if close < middle and (not array.get(shortPartialClose, i)) and (not na(array.get(idsShort, i))):
            id = array.get(idsShort, i)
            strategy.close(id=id, qty=posSize / 2)
            array.set(shortPartialClose, i, True)
    plot(middle, color=color.new(color.yellow, 0))
    plot(upper, color=color.new(color.yellow, 0))
    plot(lower, color=color.new(color.yellow, 0))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
