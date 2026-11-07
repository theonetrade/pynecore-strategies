"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_method import method, method_call
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    array, input, map, na, order, runtime, script, strategy, string, syminfo,
    ticker, time_close, timeframe, timestamp
)
from pynecore.types import IBPersistent, Persistent


@udt
class Trade:
    tickerId: str = na(str)
    isBuy: bool = na(bool)
    qty: float = na(float)
    price: float = na(float)
    execTime: int = na(int)


@script.strategy("Trading Report Generator from CSV", margin_long=0, margin_short=0, overlay=True)
def main(
    tradesCSV=input.text_area(title="Transactions CSV:", defval="Symbol,Side,Qty,Fill Price,Closing Time\nCRYPTO:BTCUSD,Buy,200,107900,2025-07-08 01:59:29\nCRYPTO:BTCUSD,Sell,100,123000,2025-07-14 07:00:00\nCRYPTO:BTCUSD,Sell,100,115000,2025-07-25 07:00:00")
):
    supportedHeader1: Persistent[str] = "Symbol,Side,Qty,Fill Price,Commission,Closing Time"
    supportedHeader2: Persistent[str] = "Symbol,Side,Qty,Fill Price,Closing Time"

    @method
    def tostring(this: Trade):
        return string.format('{0} {1} {2} shares at {3}', 'buy' if this.isBuy else 'sell', this.tickerId, this.qty, this.price)

    def parseTimestamp(timeStamp: str):
        parts = string.split(timeStamp, ' ')
        date = string.split(method_call('get', parts, 0), '-')
        y = string.tonumber(method_call('get', date, 0))
        m = string.tonumber(method_call('get', date, 1))
        d = string.tonumber(method_call('get', date, 2))

        tm = string.split(method_call('get', parts, 1), ':')
        h = string.tonumber(method_call('get', tm, 0))
        min = string.tonumber(method_call('get', tm, 1))
        s = string.tonumber(method_call('get', tm, 2))

        return timestamp(cast_int(y), cast_int(m), cast_int(d), cast_int(h), cast_int(min), cast_int(s))

    def checkSize(elems: list[str], minCount: int, lineNumber: int):
        __block_result__ = na
        if array.size(elems) < minCount:
            __block_result__ = runtime.error(string.format('Expected {0} values, founded less: {1} on the line with number {2}', minCount, elems, lineNumber))
        return __block_result__

    def parseTrade(ln: str, lineNumber: int, header1: bool):
        elems = string.split(string.trim(ln), ',')
        ticker__ren__ = method_call('get', elems, 0)
        isTrade = ticker__ren__ != '$CASH'
        __block_result_1__ = na
        if isTrade:
            checkSize(elems, 6 if header1 else 5, lineNumber)
            qty = string.tonumber(method_call('get', elems, 2))
            price = string.tonumber(method_call('get', elems, 3))
            tm = parseTimestamp(method_call('get', elems, 5 if header1 else 4))
            __block_result_1__ = Trade(ticker__ren__, string.lower(method_call('get', elems, 1)) == 'buy', qty, price, tm)
        return __block_result_1__

    mainTicker: Persistent = ticker.standard(syminfo.tickerid)

    def parseTrades():
        result: dict[int, Trade] = map.new()
        lines = string.split(tradesCSV, '\n')
        if method_call('size', lines) > 0:
            header = string.trim(method_call('get', lines, 0))
            if header != supportedHeader1 and header != supportedHeader2:
                runtime.error('Unsupported csv format. Expecting csv with columns: "' + supportedHeader1 + '" or "' + supportedHeader2 + '"\nFounded "' + header + '"')
            for i in pine_range(1, method_call('size', lines) - 1):
                t = parseTrade(method_call('get', lines, i), i + 1, header == supportedHeader1)
                if not na(t) and mainTicker == t.tickerId:
                    map.put(result, t.execTime, t)
        return result

    trades: Persistent = parseTrades()

    def sortedKeys():
        result = method_call('keys', trades)
        method_call('sort', result, order.descending)
        return result

    times: Persistent = sortedKeys()

    barDurationMs: Persistent = timeframe.in_seconds('') * 1000

    def nextId():
        uniqueId: IBPersistent[int] = 0
        uniqueId += 1
        return string.tostring(uniqueId)

    while method_call('size', times) > 0:
        firstT = method_call('last', times)
        if time_close + barDurationMs > firstT:
            first = method_call('remove', trades, firstT)
            strategy.order(id=('buy ' if first.isBuy else 'sell ') + nextId(), direction=strategy.long if first.isBuy else strategy.short, qty=first.qty, limit=first.price, comment='buy' if first.isBuy else 'sell')
            method_call('pop', times)
            continue
        else:
            break


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
