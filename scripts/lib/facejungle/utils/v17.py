"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_loop, pine_range
from pynecore.core.pine_export import Exported, export
from pynecore.lib import close, math, na, nz, script, strategy, string, syminfo, ta, volume
from pynecore.types import Series
from typing import Protocol, Any


__all__ = ['avgOpenPositionPrice', 'barCrossoverCounter', 'barCrossunderCounter', 'commentOrderCustomseries', 'commentTriggerCustomseries', 'counterEvent', 'fj_stdev', 'maCustomseries', 'okxAlertMsg']


class _ProtocolMacustomseries(Protocol):
    def __call__(self, source: float = close, typeMa: str = 'sma', length: Series[int] = ..., offset: float = 0.85, sigma: int = 6) -> Any: ...


class _ProtocolFjStdev(Protocol):
    def __call__(self, src: float, length: int, mult: float, middleType: str) -> Any: ...


class _ProtocolCounterevent(Protocol):
    def __call__(self, enent: bool, enent2: bool) -> Any: ...


class _ProtocolBarcrossovercounter(Protocol):
    def __call__(self, signalPrice: float, basePrice: float) -> Any: ...


class _ProtocolBarcrossundercounter(Protocol):
    def __call__(self, signalPrice: float, basePrice: float) -> Any: ...


class _ProtocolAvgopenpositionprice(Protocol):
    def __call__(self, ) -> Any: ...


class _ProtocolOkxalertmsg(Protocol):
    def __call__(self, action: str, signalToken: str, orderType: str, orderPriceOffset: str, investmentType: str, amount: str) -> Any: ...


class _ProtocolCommenttriggercustomseries(Protocol):
    def __call__(self, trigger: str) -> Any: ...


class _ProtocolCommentordercustomseries(Protocol):
    def __call__(self, reason: str, trigger: str = na, tradeNo: int = na, qty: float = na) -> Any: ...


maCustomseries: _ProtocolMacustomseries = Exported()
fj_stdev: _ProtocolFjStdev = Exported()
counterEvent: _ProtocolCounterevent = Exported()
barCrossoverCounter: _ProtocolBarcrossovercounter = Exported()
barCrossunderCounter: _ProtocolBarcrossundercounter = Exported()
avgOpenPositionPrice: _ProtocolAvgopenpositionprice = Exported()
okxAlertMsg: _ProtocolOkxalertmsg = Exported()
commentTriggerCustomseries: _ProtocolCommenttriggercustomseries = Exported()
commentOrderCustomseries: _ProtocolCommentordercustomseries = Exported()


@script.library('utils', True)
def main():
    def pine_ema(src, length):
        alpha = 2 / (length + 1)
        sum: Series[float] = 0.0
        sum = src if na(sum[1]) else alpha * src + (1 - alpha) * nz(sum[1])
        return sum

    def pine_sma(x: Series, y):
        sum: float = 0.0
        for i in pine_range(0, y - 1, 1):
            sum = sum + x[i] / y
        return sum

    def pine_rma(src, length):
        alpha = 1 / length
        sum: Series[float] = 0.0
        sma = pine_sma(src, length)
        sum = sma if na(sum[1]) else alpha * src + (1 - alpha) * nz(sum[1])
        return sum

    def pine_wma(x: Series, y):
        norm: float = 0.0
        sum: float = 0.0
        for i in pine_range(0, y - 1, 1):
            weight = (y - i) * y
            norm = norm + weight
            sum = sum + x[i] * weight
        return sum / norm

    def pine_hma(src, length):
        return pine_wma(2 * pine_wma(src, length / 2) - pine_wma(src, length), math.round(math.sqrt(length)))

    def pine_vwma(x, y):
        return pine_sma(x * volume, y) / pine_sma(volume, y)

    def pine_swma(x: Series):
        return x[3] * 1 / 6 + x[2] * 2 / 6 + x[1] * 2 / 6 + x * 1 / 6

    def pine_alma(series: Series, windowsize, offset, sigma):
        m = math.floor(offset * (windowsize - 1))
        s = windowsize / sigma
        norm: float = 0.0
        sum: float = 0.0
        for i in pine_range(0, windowsize - 1, 1):
            weight = math.exp(-1 * math.pow(i - m, 2) / (2 * math.pow(s, 2)))
            norm = norm + weight
            sum = sum + series[windowsize - i - 1] * weight
        return sum / norm

    def pine_dema(src, length):
        ema = pine_ema(src, length)
        return 2 * ema - pine_ema(ema, length)

    def pine_tema(src, length):
        ema = pine_ema(src, length)
        return 3 * (ema - pine_ema(ema, length)) + pine_ema(pine_ema(ema, length), length)

    def pine_smma(src, length):
        sum: Series[float] = 0.0
        sma = pine_sma(src, length)
        return sma if na(sum[1]) else (sum[1] * (length - 1) + src) / length

    def pine_ssma(src: Series, length):
        a1 = math.exp(-1.414 * 3.14159 / length)
        b1 = 2 * a1 * math.cos(1.414 * 3.14159 / length)
        c2 = b1
        c3 = -a1 * a1
        c1 = 1 - c2 - c3
        sum: Series[float] = 0.0
        sum = c1 * (src + nz(src[1])) / 2 + c2 * nz(sum[1]) + c3 * nz(sum[2])
        return sum

    @export
    def maCustomseries(source: float = close, typeMa: str = 'sma', length: Series[int] = na, offset: float = 0.85, sigma: int = 6):
        __block_result__ = na
        __switch__ = typeMa
        if __switch__ == 'alma':
            __block_result__ = pine_alma(source, length, offset, sigma)
        elif __switch__ == 'ema':
            __block_result__ = pine_ema(source, length)
        elif __switch__ == 'tema':
            __block_result__ = pine_dema(source, length)
        elif __switch__ == 'dema':
            __block_result__ = pine_tema(source, length)
        elif __switch__ == 'sma':
            __block_result__ = pine_sma(source, length)
        elif __switch__ == 'smma':
            __block_result__ = pine_smma(source, length)
        elif __switch__ == 'ssma':
            __block_result__ = pine_ssma(source, length)
        elif __switch__ == 'rma':
            __block_result__ = pine_rma(source, length)
        elif __switch__ == 'hma':
            __block_result__ = pine_hma(source, length)
        elif __switch__ == 'wma':
            __block_result__ = pine_wma(source, length)
        elif __switch__ == 'vwma':
            __block_result__ = pine_vwma(source, length)
        elif __switch__ == 'swma':
            __block_result__ = pine_swma(source)
        elif __switch__ == 'linreg':
            __block_result__ = ta.linreg(source, length, sigma)
        elif __switch__ == 'median':
            __block_result__ = ta.median(source, length)
        elif __switch__ == 'mom':
            __block_result__ = ta.mom(source, length)
        elif __switch__ == 'high':
            __block_result__ = ta.highest(source, length)
        elif __switch__ == 'low':
            __block_result__ = ta.lowest(source, length)
        elif __switch__ == 'medianHigh':
            __block_result__ = ta.median(ta.highest(source, length), length)
        elif __switch__ == 'medianLow':
            __block_result__ = ta.median(ta.lowest(source, length), length)
        elif __switch__ == 'percentrank':
            __block_result__ = ta.percentrank(source, length)
        else:
            __block_result__ = (ta.highest(length) + ta.lowest(length)) / 2
        return __block_result__

    @export
    def fj_stdev(src: float, length: int, mult: float, middleType: str):
        basis: float = maCustomseries(src, middleType, length)
        dev: float = mult * ta.stdev(src, length)
        dev2: float = mult * ta.stdev(src, length) * 0.618
        dev3: float = mult * ta.stdev(src, length) * 1.618
        dev4: float = mult * ta.stdev(src, length) * 2.618
        return (basis, basis + dev2, basis + dev, basis + dev3, basis + dev4, basis - dev2, basis - dev, basis - dev3, basis - dev4)

    @export
    def counterEvent(enent: bool, enent2: bool):
        scount: Series[int] = 0
        scount = nz(scount[1]) + 1 if enent and enent2 else 0
        return scount

    @export
    def barCrossoverCounter(signalPrice: float, basePrice: float):
        bcond: bool = signalPrice > basePrice
        bcount: Series[int] = 0
        bcount = nz(bcount[1]) + 1 if bcond else 0
        return bcount

    @export
    def barCrossunderCounter(signalPrice: float, basePrice: float):
        scond: bool = signalPrice < basePrice
        scount: Series[int] = 0
        scount = nz(scount[1]) + 1 if scond else 0
        return scount

    @export
    def avgOpenPositionPrice():
        sumOpenPositionPrice: float = 0.0
        __loop_0__ = pine_loop(0, 1)
        while __loop_0__.step(strategy.opentrades - 1):
            tradeNo = __loop_0__.value
            sumOpenPositionPrice = sumOpenPositionPrice + strategy.opentrades.entry_price(tradeNo) * strategy.opentrades.size(tradeNo) / strategy.position_size
        result = nz(sumOpenPositionPrice / strategy.opentrades)
        return result

    @export
    def okxAlertMsg(action: str, signalToken: str, orderType: str, orderPriceOffset: str, investmentType: str, amount: str):
        str__ren__: str = '{'
        str__ren__ = str__ren__ + '"action": "' + action + '", '
        str__ren__ = str__ren__ + '"instrument": "' + syminfo.ticker + '", '
        str__ren__ = str__ren__ + '"signalToken": "' + signalToken + '", '
        str__ren__ = str__ren__ + '"timestamp": "{{timenow}}", '
        str__ren__ = str__ren__ + '"maxLag": "180", '
        str__ren__ = str__ren__ + '"orderType": "' + orderType + '", '
        str__ren__ = str__ren__ + '"orderPriceOffset": "' + string.tostring(orderPriceOffset) + '", '
        str__ren__ = str__ren__ + '"investmentType": "' + investmentType + '", '
        str__ren__ = str__ren__ + '"amount": "' + string.tostring(amount) + '"'
        str__ren__ = str__ren__ + '}'
        return str__ren__

    @export
    def commentTriggerCustomseries(trigger: str):
        __block_result_1__ = na
        __switch__ = trigger
        if __switch__ == 'supertrend':
            __block_result_1__ = 'SuperTrend change direction'
        elif __switch__ == 'bbUpper':
            __block_result_1__ = 'price crossing BB upper'
        elif __switch__ == 'bbUpper2':
            __block_result_1__ = 'price crossing BB upper 2'
        elif __switch__ == 'bbUpper3':
            __block_result_1__ = 'price crossing BB upper 3'
        elif __switch__ == 'bbLower':
            __block_result_1__ = 'price crossing BB lower'
        elif __switch__ == 'bbLower2':
            __block_result_1__ = 'price crossing BB lower 2'
        elif __switch__ == 'bbLower3':
            __block_result_1__ = 'price crossing BB lower 3'
        elif __switch__ == 'maBasis':
            __block_result_1__ = 'price crossing MA basis'
        elif __switch__ == 'maSignal':
            __block_result_1__ = 'price crossing MA signal'
        elif __switch__ == 'maCross':
            __block_result_1__ = 'MA signal crossing MA basis'
        elif __switch__ == 'stop':
            __block_result_1__ = 'price crossing stop line'
        else:
            __block_result_1__ = ''
        return __block_result_1__

    @export
    def commentOrderCustomseries(reason: str, trigger: str = na, tradeNo: int = na, qty: float = na):
        msg: str = ''
        if reason == 'enter_long':
            msg = msg + '↗️[Entry] Long'
            msg = msg + (' #' + string.tostring(tradeNo) if na(tradeNo) == False else na)
            msg = msg + (', ' + commentTriggerCustomseries(trigger) if na(trigger) == False else na)
        if reason == 'enter_short':
            msg = msg + '↘️[Entry] Short'
            msg = msg + (' #' + string.tostring(tradeNo) if na(tradeNo) == False else na)
            msg = msg + (', ' + commentTriggerCustomseries(trigger) if na(trigger) == False else na)
        if reason == 'take_long':
            msg = msg + '💲[TP] Long'
            msg = msg + (' ' + string.tostring(qty, '#.###') + '%' if na(qty) == False else na)
            msg = msg + (', ' + commentTriggerCustomseries(trigger) if na(trigger) == False else na)
        if reason == 'take_short':
            msg = msg + '💲[TP] Short'
            msg = msg + (' ' + string.tostring(qty, '#.###') + '%' if na(qty) == False else na)
            msg = msg + (', ' + commentTriggerCustomseries(trigger) if na(trigger) == False else na)
        if reason == 'stop_long':
            msg = msg + '✖️[SL] Long'
            msg = msg + (', ' + commentTriggerCustomseries(trigger) if na(trigger) == False else na)
        if reason == 'stop_short':
            msg = msg + '✖️[SL] Short'
            msg = msg + (', ' + commentTriggerCustomseries(trigger) if na(trigger) == False else na)
        result = msg
        return result


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
