"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_loop, pine_range
from pynecore.core.overload import overload
from pynecore.core.pine_export import Exported, export
from pynecore.core.series import inline_series
from pynecore.lib import (
    array, bar_index, close, color, fixnan, high, hl2, label, low, math, na,
    nz, runtime, script, size, strategy, string, syminfo, ta, text, time, timeframe, volume, xloc
)
from pynecore.types import Label, Persistent, PersistentSeries, Series
from typing import Protocol, Any


__all__ = ['checkVar', 'closeUnfilledEntriesAfter', 'convertTimeframeToString', 'formatEntryPrices', 'getAlertatronAlertMessageMarketClosePercentOfPosition', 'getAlertatronEntryMessage', 'getAlertatronEntryMessageV2', 'getAlertatronExitMessage', 'getAlertatronMarketEntryMessage', 'getAlertatronMarketExitMessage', 'getAlertatronOcoMessage', 'getAlertatrongAlertMessages', 'getAllTradeIDs', 'getAveragePriceOfFilledLadders', 'getBaseCurrency', 'getChartSymbol', 'getClosedTradeSince', 'getContractCount', 'getCountOfClosedTradeSince', 'getDecimals', 'getEntryNames', 'getLadderInSteps', 'getLadderOutSteps', 'getLockedLadderStart', 'getLotSize', 'getOpenTradeIDs', 'getPairDividerForExchange', 'getPairOverrides', 'getRateOfChange', 'getStrategyAlertMessage', 'isBetweenTwoTimes', 'orderAlreadyClosedSince', 'orderAlreadyExists', 'orderCurrentlyExists', 'taGetAdx', 'taGetDirectionalIndex', 'taGetEma', 'taGetExtremes', 'taGetPercentDif', 'taGetResistance', 'taGetSupport', 'taGetVwap']


class _ProtocolGetbasecurrency(Protocol):
    def __call__(self, ) -> Any: ...


class _ProtocolGetchartsymbol(Protocol):
    def __call__(self, ) -> Any: ...


class _ProtocolGetdecimals(Protocol):
    def __call__(self, ) -> Any: ...


class _ProtocolCheckvar(Protocol):
    def __call__(self, y_offset: int, variable: str) -> Any: ...


class _ProtocolGetpairdividerforexchange(Protocol):
    def __call__(self, exchangeName: str) -> Any: ...


class _ProtocolGetstrategyalertmessage(Protocol):
    def __call__(self, secret: str, symbol: str, base_currency: str, side: str, orderTriggerPrice: float, orderLimitPrice: float, orderSize: str, profitTriggerPrice: float, profitLimitPrice: float, stopLossTriggerPrice: float, stopLossLimitPrice: float, cancelExistingUnfilledOrders: bool) -> Any: ...


class _ProtocolGetalertatronentrymessage(Protocol):
    def __call__(self, strategyName: str, secret: str, leverage: int, leverageType: str, symbol: str, baseCurrency: str, pairDivider: str, side: str, orderPrice: float, orderSize: str, stopLossPrice: float, cancelExistingUnfilledOrders: bool) -> Any: ...


class _ProtocolGetalertatronexitmessage(Protocol):
    def __call__(self, strategyName: str, secret: str, symbol: str, baseCurrency: str, pairDivider: str, side: str, orderPrice: float, orderSize: str, cancelExistingUnfilledOrders: bool) -> Any: ...


class _ProtocolGetalertatronentrymessagev2(Protocol):
    def __call__(self, tag: str, secret: str, leverage: int, leverageType: str, symbol: str, baseCurrency: str, pairDivider: str, side: str, entryPrices: str, entrySizes: str, profitTargetPrices: str, profitTargetSizes: str, stopLossPrice: float, cancelExistingUnfilledOrders: bool) -> Any: ...


class _ProtocolTagetadx(Protocol):
    def __call__(self, diLength: int, smoothing: int) -> Any: ...


class _ProtocolTagetdirectionalindex(Protocol):
    def __call__(self, length: int) -> Any: ...


class _ProtocolTagetdirectionalindex11(Protocol):
    def __call__(self, diLength: float) -> Any: ...


class _ProtocolTagetema(Protocol):
    def __call__(self, type: str, source: Series[float], length: int) -> Any: ...


class _ProtocolTagetvwap(Protocol):
    def __call__(self, src: float, anchor: str, multiplier: float) -> Any: ...


class _ProtocolTagetextremes(Protocol):
    def __call__(self, value: float, direction: str, lookbackPeriod: int, sampleSize: int) -> Any: ...


class _ProtocolTagetsupport(Protocol):
    def __call__(self, lookback: int, lookahead: int) -> Any: ...


class _ProtocolTagetresistance(Protocol):
    def __call__(self, lookback: int, lookahead: int) -> Any: ...


class _ProtocolTagetpercentdif(Protocol):
    def __call__(self, number1: float, number2: float) -> Any: ...


class _ProtocolIsbetweentwotimes(Protocol):
    def __call__(self, session__ren__: str, timezone: str) -> Any: ...


class _ProtocolGetalltradeids(Protocol):
    def __call__(self, ) -> Any: ...


class _ProtocolGetclosedtradesince(Protocol):
    def __call__(self, barNumberToCompare: int) -> Any: ...


class _ProtocolGetcountofclosedtradesince(Protocol):
    def __call__(self, barNumberToCompare: int) -> Any: ...


class _ProtocolOrderalreadyclosedsince(Protocol):
    def __call__(self, exitId: str, barNumberToCompare: int) -> Any: ...


class _ProtocolGetopentradeids(Protocol):
    def __call__(self, ) -> Any: ...


class _ProtocolOrderalreadyexists(Protocol):
    def __call__(self, order_id: str) -> Any: ...


class _ProtocolOrdercurrentlyexists(Protocol):
    def __call__(self, order_id: str) -> Any: ...


class _ProtocolGetlockedladderstart(Protocol):
    def __call__(self, startingLadderPrice: float) -> Any: ...


class _ProtocolGetaveragepriceoffilledladders(Protocol):
    def __call__(self, ) -> Any: ...


class _ProtocolGetcontractcount(Protocol):
    def __call__(self, amount: str, price: float) -> Any: ...


class _ProtocolGetladderinsteps(Protocol):
    def __call__(self, side: str, amount: float, amountType: str, ladderRungs: int, ladderStart: float, ladderStop: float, stepSpacingPercent: float, roundTo: int) -> Any: ...


class _ProtocolGetladderoutsteps(Protocol):
    def __call__(self, side: str, ladderStart: float, ladderRungs: int, stepSpacingPercent: float, roundTo: int) -> Any: ...


class _ProtocolGetrateofchange(Protocol):
    def __call__(self, source: float, length: int) -> Any: ...


class _ProtocolCloseunfilledentriesafter(Protocol):
    def __call__(self, cancelUnfilledOrdersAfter: int, cancelUnfilledOrdersType: str, startingBar: int) -> Any: ...


class _ProtocolGetentrynames(Protocol):
    def __call__(self, numberOfEntries: int, side: str) -> Any: ...


class _ProtocolFormatentryprices(Protocol):
    def __call__(self, entryPrices: str) -> Any: ...


class _ProtocolGetlotsize(Protocol):
    def __call__(self, type: str, amount: float, leverage: float, roundTo: int) -> Any: ...


class _ProtocolGetpairoverrides(Protocol):
    def __call__(self, symbolOverride: str, currencyOverride: str) -> Any: ...


class _ProtocolGetalertatrongalertmessages(Protocol):
    def __call__(self, tag: str, secret: str, symbol: str, baseCurrency: str, pairDivider: str, side: str, symbolMaxDecimals: int, leverage: int, leverageType: str, entryPrices: list[float], entryAmounts: list[float], entryAmountType: str, profitTargets: list[float], profitTargetType: str, profitTargetAmounts: list[float], stopTrigger: float, stopTriggerType: str, stopLimitOffset: float, trailingStopTrigger: float, trailingStopTriggerType: str, trailingStopLimitOffset: float) -> Any: ...


class _ProtocolGetalertatronmarketentrymessage(Protocol):
    def __call__(self, secret: str, symbol: str, baseCurrency: str, pairDivider: str, side: str, symbolMaxDecimals: int, leverage: int, leverageType: str, entryPrice: float, amount: float, amountType: str, stopTrigger: float, stopTriggerType: str, stopLimitOffset: float) -> Any: ...


class _ProtocolGetalertatronocomessage(Protocol):
    def __call__(self, secret: str, symbol: str, baseCurrency: str, pairDivider: str, side: str, symbolMaxDecimals: int, leverage: int, leverageType: str, entryPrice: float, amount: float, amountType: str, stopTrigger: float, stopTriggerType: str, stopLimitOffset: float, profitTrigger: float, profitTriggerType: str, profitLimitOffset: float) -> Any: ...


class _ProtocolGetalertatronmarketexitmessage(Protocol):
    def __call__(self, secret: str, symbol: str, baseCurrency: str, pairDivider: str, side: str) -> Any: ...


class _ProtocolGetalertatronalertmessagemarketclosepercentofposition(Protocol):
    def __call__(self, secret: str, symbol: str, baseCurrency: str, pairDivider: str, percent: int, side: str) -> Any: ...


class _ProtocolConverttimeframetostring(Protocol):
    def __call__(self, timeframe__ren__: str) -> Any: ...


getBaseCurrency: _ProtocolGetbasecurrency = Exported()
getChartSymbol: _ProtocolGetchartsymbol = Exported()
getDecimals: _ProtocolGetdecimals = Exported()
checkVar: _ProtocolCheckvar = Exported()
getPairDividerForExchange: _ProtocolGetpairdividerforexchange = Exported()
getStrategyAlertMessage: _ProtocolGetstrategyalertmessage = Exported()
getAlertatronEntryMessage: _ProtocolGetalertatronentrymessage = Exported()
getAlertatronExitMessage: _ProtocolGetalertatronexitmessage = Exported()
getAlertatronEntryMessageV2: _ProtocolGetalertatronentrymessagev2 = Exported()
taGetAdx: _ProtocolTagetadx = Exported()
taGetDirectionalIndex: _ProtocolTagetdirectionalindex = Exported()
taGetDirectionalIndex: _ProtocolTagetdirectionalindex11 = Exported()
taGetEma: _ProtocolTagetema = Exported()
taGetVwap: _ProtocolTagetvwap = Exported()
taGetExtremes: _ProtocolTagetextremes = Exported()
taGetSupport: _ProtocolTagetsupport = Exported()
taGetResistance: _ProtocolTagetresistance = Exported()
taGetPercentDif: _ProtocolTagetpercentdif = Exported()
isBetweenTwoTimes: _ProtocolIsbetweentwotimes = Exported()
getAllTradeIDs: _ProtocolGetalltradeids = Exported()
getClosedTradeSince: _ProtocolGetclosedtradesince = Exported()
getCountOfClosedTradeSince: _ProtocolGetcountofclosedtradesince = Exported()
orderAlreadyClosedSince: _ProtocolOrderalreadyclosedsince = Exported()
getOpenTradeIDs: _ProtocolGetopentradeids = Exported()
orderAlreadyExists: _ProtocolOrderalreadyexists = Exported()
orderCurrentlyExists: _ProtocolOrdercurrentlyexists = Exported()
getLockedLadderStart: _ProtocolGetlockedladderstart = Exported()
getAveragePriceOfFilledLadders: _ProtocolGetaveragepriceoffilledladders = Exported()
getContractCount: _ProtocolGetcontractcount = Exported()
getLadderInSteps: _ProtocolGetladderinsteps = Exported()
getLadderOutSteps: _ProtocolGetladderoutsteps = Exported()
getRateOfChange: _ProtocolGetrateofchange = Exported()
closeUnfilledEntriesAfter: _ProtocolCloseunfilledentriesafter = Exported()
getEntryNames: _ProtocolGetentrynames = Exported()
formatEntryPrices: _ProtocolFormatentryprices = Exported()
getLotSize: _ProtocolGetlotsize = Exported()
getPairOverrides: _ProtocolGetpairoverrides = Exported()
getAlertatrongAlertMessages: _ProtocolGetalertatrongalertmessages = Exported()
getAlertatronMarketEntryMessage: _ProtocolGetalertatronmarketentrymessage = Exported()
getAlertatronOcoMessage: _ProtocolGetalertatronocomessage = Exported()
getAlertatronMarketExitMessage: _ProtocolGetalertatronmarketexitmessage = Exported()
getAlertatronAlertMessageMarketClosePercentOfPosition: _ProtocolGetalertatronalertmessagemarketclosepercentofposition = Exported()
convertTimeframeToString: _ProtocolConverttimeframetostring = Exported()


@script.library('threengine_global_automation_library', na_bool=True)
def main():
    @export
    def getBaseCurrency():
        ticker__ren__: Persistent = syminfo.ticker
        base_currency: Persistent[str] = na(str)
        if string.endswith(ticker__ren__, 'USDT'):
            base_currency = 'USDT'
        else:
            if string.endswith(ticker__ren__, 'USDT.P'):
                base_currency = 'USDT'
            else:
                if string.endswith(ticker__ren__, 'USDC'):
                    base_currency = 'USDC'
                else:
                    if string.endswith(ticker__ren__, 'BUSD'):
                        base_currency = 'BUSD'
                    else:
                        if string.endswith(ticker__ren__, 'BTC'):
                            base_currency = 'BTC'
                        else:
                            if string.endswith(ticker__ren__, 'PERP'):
                                base_currency = 'PERP'
                            else:
                                if string.endswith(ticker__ren__, 'USD'):
                                    base_currency = 'USD'
                                else:
                                    if string.endswith(ticker__ren__, 'USD.P'):
                                        base_currency = 'USD'
                                    else:
                                        base_currency = 'USD'
        return base_currency

    @export
    def getChartSymbol():
        ticker__ren__: Persistent = syminfo.ticker
        trade_pair_parts: list[str] = array.new_string()
        trade_pair: Persistent[str] = na(str)
        if string.endswith(ticker__ren__, 'USDT'):
            trade_pair_parts = string.split(ticker__ren__, 'USDT')
            trade_pair = array.get(trade_pair_parts, 0)
        else:
            if string.endswith(ticker__ren__, 'USDT.P'):
                trade_pair_parts = string.split(ticker__ren__, 'USDT.P')
                trade_pair = array.get(trade_pair_parts, 0)
            else:
                if string.endswith(ticker__ren__, 'USDC'):
                    trade_pair_parts = string.split(ticker__ren__, 'USDC')
                    trade_pair = array.get(trade_pair_parts, 0)
                else:
                    if string.endswith(ticker__ren__, 'BUSD'):
                        trade_pair_parts = string.split(ticker__ren__, 'BUSD')
                        trade_pair = array.get(trade_pair_parts, 0)
                    else:
                        if string.endswith(ticker__ren__, 'BTC'):
                            trade_pair_parts = string.split(ticker__ren__, 'BTC')
                            trade_pair = array.get(trade_pair_parts, 0)
                        else:
                            if string.endswith(ticker__ren__, 'PERP'):
                                trade_pair_parts = string.split(ticker__ren__, 'PERP')
                                trade_pair = array.get(trade_pair_parts, 0)
                            else:
                                if string.endswith(ticker__ren__, 'USD'):
                                    trade_pair_parts = string.split(ticker__ren__, 'USD')
                                    trade_pair = array.get(trade_pair_parts, 0)
                                else:
                                    if string.endswith(ticker__ren__, 'USD.P'):
                                        trade_pair_parts = string.split(ticker__ren__, 'USD.P')
                                        trade_pair = array.get(trade_pair_parts, 0)
                                    else:
                                        trade_pair = ticker__ren__
        return trade_pair

    @export
    def getDecimals():
        return math.abs(math.log(syminfo.mintick) / math.log(10))

    @export
    def checkVar(y_offset: int, variable: str):
        lb: Persistent[Label] = na(Label)
        label.delete(lb)
        lb = label.new(x=time + 20000000, xloc=xloc.bar_time, y=hl2 + y_offset, style=label.style_none, size=size.normal, textcolor=color.new(color.blue, 0), textalign=text.align_left, text=string.tostring(variable))
        return lb

    @export
    def getPairDividerForExchange(exchangeName: str):
        __block_result__ = na
        __switch__ = exchangeName
        if __switch__ == 'FTX.us':
            __block_result__ = '/'
        elif __switch__ == 'ByBit':
            __block_result__ = ''
        else:
            __block_result__ = na
        pairDivider = __block_result__
        return pairDivider

    @export
    def getStrategyAlertMessage(secret: str, symbol: str, base_currency: str, side: str, orderTriggerPrice: float, orderLimitPrice: float, orderSize: str, profitTriggerPrice: float, profitLimitPrice: float, stopLossTriggerPrice: float, stopLossLimitPrice: float, cancelExistingUnfilledOrders: bool):
        __block_result_1__ = na
        if side == 'buy':
            __block_result_1__ = 'sell'
        else:
            __block_result_1__ = 'buy'
        close_side = __block_result_1__
        return '{' + '"secret" : "' + string.tostring(secret) + '", ' + '"symbol" : "' + string.tostring(symbol) + '", ' + '"baseCurrency" : "' + string.tostring(base_currency) + '", ' + '"cancelExistingUnfilledOrders" : ' + string.tostring(cancelExistingUnfilledOrders) + ', ' + '"order" : {' + '"side" : "' + string.tostring(side) + '", ' + '"triggerPrice" : ' + string.tostring(orderTriggerPrice) + ', ' + '"limitPrice" : ' + string.tostring(orderLimitPrice) + ', ' + '"size" : "' + string.tostring(orderSize) + '"' + '}, "takeProfit" : {' + '"side" : "' + string.tostring(close_side) + '", ' + '"triggerPrice" : ' + string.tostring(profitTriggerPrice) + ', ' + '"limitPrice" : ' + string.tostring(profitLimitPrice) + ', ' + '"size" : "100%p"' + '}, "stopLoss" : {' + '"side" : "' + string.tostring(close_side) + '", ' + '"triggerPrice" : ' + string.tostring(stopLossTriggerPrice) + ', ' + '"limitPrice" : ' + string.tostring(stopLossLimitPrice) + ', ' + '"size" : "100%p"' + '},"chartInfo" : {' + '"barIndex" : "' + string.tostring(bar_index + 1) + '", ' + '"time" : "' + string.tostring(time) + '", ' + '"decimals" : "' + string.tostring(getDecimals()) + '"' + '}' + '}'

    @export
    def getAlertatronEntryMessage(strategyName: str, secret: str, leverage: int, leverageType: str, symbol: str, baseCurrency: str, pairDivider: str, side: str, orderPrice: float, orderSize: str, stopLossPrice: float, cancelExistingUnfilledOrders: bool):
        closeSide = 'sell' if side == 'buy' else 'buy'
        initializeOrder: str = string.tostring(secret) + '(' + string.tostring(symbol) + pairDivider + string.tostring(baseCurrency) + ') { '
        exchangeSettings: str = 'exchangeSettings(leverage=' + string.tostring(leverage) + '); ' + 'exchangeSettings(leverage=' + string.lower(leverageType) + '); '
        cancelOrders: str = 'cancel(which=all); ' if cancelExistingUnfilledOrders else ''
        limit: str = 'limit(side=' + string.tostring(side) + ', amount=' + string.tostring(orderSize) + ', offset=@' + string.tostring(orderPrice) + '); '
        stopLoss: str = 'stopOrder(side=' + string.tostring(closeSide) + ', amount=' + string.tostring(orderSize) + ', offset=@' + string.tostring(stopLossPrice) + ', trigger=last, reduceOnly=true); '
        messageEnd: str = '} #bot '
        comment: str = '// Alert Source: ' + string.tostring(strategyName)
        webhookEntryMessage = initializeOrder + exchangeSettings + cancelOrders + limit + stopLoss + messageEnd + comment
        return webhookEntryMessage

    @export
    def getAlertatronExitMessage(strategyName: str, secret: str, symbol: str, baseCurrency: str, pairDivider: str, side: str, orderPrice: float, orderSize: str, cancelExistingUnfilledOrders: bool):
        initializeOrder: str = string.tostring(secret) + '(' + string.tostring(symbol) + pairDivider + string.tostring(baseCurrency) + ') { '
        cancelOrders: str = 'cancel(which=all); ' if cancelExistingUnfilledOrders else ''
        limit: str = 'limit(side=' + string.tostring(side) + ', amount=' + string.tostring(orderSize) + ', offset=@' + string.tostring(orderPrice) + ', reduceOnly=true); '
        messageEnd: str = '} #bot '
        comment: str = '// Alert Source: ' + string.tostring(strategyName)
        webhookExitMessage = initializeOrder + cancelOrders + limit + messageEnd + comment
        return webhookExitMessage

    @export
    def getAlertatronEntryMessageV2(tag: str, secret: str, leverage: int, leverageType: str, symbol: str, baseCurrency: str, pairDivider: str, side: str, entryPrices: str, entrySizes: str, profitTargetPrices: str, profitTargetSizes: str, stopLossPrice: float, cancelExistingUnfilledOrders: bool):
        closeSide: str = 'sell' if side == 'buy' else 'buy'
        entryPricesArray = string.split(entryPrices, ',')
        entrySizessArray = string.split(entrySizes, ',')
        profitTargetPricesArray = string.split(profitTargetPrices, ',')
        profitTargetSizesArray = string.split(profitTargetSizes, ',')
        webhookEntryMessages: str = ''
        __block_result_2__ = na
        for i in pine_range(0, array.size(entryPricesArray) - 1, 1):
            initializeOrder: str = string.tostring(secret) + '(' + string.tostring(symbol) + pairDivider + string.tostring(baseCurrency) + ') { '
            exchangeSettings: str = 'exchangeSettings(leverage=' + string.tostring(leverage) + '); ' + 'exchangeSettings(leverage=' + string.lower(leverageType) + '); '
            cancelOrders: str = 'cancel(which=tagged, tag=' + tag + '); ' if cancelExistingUnfilledOrders else ''
            waitingLimit: str = 'waitingLimit(side=' + string.tostring(side) + ', amount=' + string.tostring(array.get(entrySizessArray, i)) + ', offset=@' + string.tostring(array.get(entryPricesArray, i)) + ", tag='" + tag + "'); "
            profitTargets: str = ''
            for x in pine_range(0, array.size(profitTargetPricesArray) - 1, 1):
                profitTarget = 'limit(side=' + closeSide + ', amount=' + string.tostring(array.get(profitTargetSizesArray, x)) + ', offset=@' + string.tostring(array.get(profitTargetPricesArray, x)) + ", reduceOnly=true, tag='" + tag + "'); "
                profitTargets = profitTargets + profitTarget
            stopLoss: str = 'stopOrder(side=' + string.tostring(closeSide) + ', amount=' + string.tostring(array.get(profitTargetSizesArray, i)) + ', offset=@' + string.tostring(stopLossPrice) + ", trigger=last, reduceOnly=true, tag='" + tag + "'); "
            messageEnd: str = '} #bot '
            webhookEntryMessage = initializeOrder + exchangeSettings + cancelOrders + waitingLimit + profitTargets + stopLoss + messageEnd
            webhookEntryMessages = webhookEntryMessages + webhookEntryMessage
            __block_result_2__ = webhookEntryMessages
        return __block_result_2__

    @export
    def taGetAdx(diLength: int, smoothing: int):
        up = ta.change(high)
        down = -ta.change(low)
        plusDm = na if na(up) else up if up > down and up > 0 else 0
        minusDm = na if na(down) else down if down > up and down > 0 else 0
        trueRange = ta.rma(ta.tr, diLength)
        plus = fixnan(100 * ta.rma(plusDm, diLength) / trueRange)
        minus = fixnan(100 * ta.rma(minusDm, diLength) / trueRange)
        sum = plus + minus
        adx = 100 * ta.rma(math.abs(plus - minus) / (1 if sum == 0 else sum), smoothing)
        return adx

    @export
    @overload
    def taGetDirectionalIndex(length: int):
        TrueRange = math.max(math.max(high - low, math.abs(high - nz(close[1]))), math.abs(low - nz(close[1])))
        DirectionalMovementPlus = math.max(high - nz(high[1]), 0) if high - nz(high[1]) > nz(low[1]) - low else 0
        DirectionalMovementMinus = math.max(nz(low[1]) - low, 0) if nz(low[1]) - low > high - nz(high[1]) else 0
        SmoothedTrueRange: Series[float] = 0.0
        SmoothedTrueRange = nz(SmoothedTrueRange[1]) - nz(SmoothedTrueRange[1]) / length + TrueRange
        SmoothedDirectionalMovementPlus: Series[float] = 0.0
        SmoothedDirectionalMovementPlus = nz(SmoothedDirectionalMovementPlus[1]) - nz(SmoothedDirectionalMovementPlus[1]) / length + DirectionalMovementPlus
        SmoothedDirectionalMovementMinus: Series[float] = 0.0
        SmoothedDirectionalMovementMinus = nz(SmoothedDirectionalMovementMinus[1]) - nz(SmoothedDirectionalMovementMinus[1]) / length + DirectionalMovementMinus
        DIPlus = SmoothedDirectionalMovementPlus / SmoothedTrueRange * 100
        DIMinus = SmoothedDirectionalMovementMinus / SmoothedTrueRange * 100
        distanceBetweenDi = (DIPlus - DIMinus) * -1 if DIPlus - DIMinus < 0 else DIPlus - DIMinus
        return (DIPlus, DIMinus, distanceBetweenDi)

    @export
    @overload
    def taGetDirectionalIndex(diLength: float):
        TrueRange = math.max(math.max(high - low, math.abs(high - nz(close[1]))), math.abs(low - nz(close[1])))
        DirectionalMovementPlus = math.max(high - nz(high[1]), 0) if high - nz(high[1]) > nz(low[1]) - low else 0
        DirectionalMovementMinus = math.max(nz(low[1]) - low, 0) if nz(low[1]) - low > high - nz(high[1]) else 0
        SmoothedTrueRange: Series[float] = 0.0
        SmoothedTrueRange = nz(SmoothedTrueRange[1]) - nz(SmoothedTrueRange[1]) / diLength + TrueRange
        SmoothedDiMovementPlus: Series[float] = 0.0
        SmoothedDiMovementPlus = nz(SmoothedDiMovementPlus[1]) - nz(SmoothedDiMovementPlus[1]) / diLength + DirectionalMovementPlus
        SmoothedDiMovementMinus: Series[float] = 0.0
        SmoothedDiMovementMinus = nz(SmoothedDiMovementMinus[1]) - nz(SmoothedDiMovementMinus[1]) / diLength + DirectionalMovementMinus
        DiPlus = SmoothedDiMovementPlus / SmoothedTrueRange * 100
        DiMinus = SmoothedDiMovementMinus / SmoothedTrueRange * 100
        DX = math.abs(DiPlus - DiMinus) / (DiPlus + DiMinus) * 100
        return (DiPlus, DiMinus)

    @export
    def taGetEma(type: str, source: Series[float], length: int):
        __block_result_3__ = na
        __switch__ = type
        if __switch__ == 'EMA':
            __block_result_3__ = ta.ema(source, length)
        elif __switch__ == 'SMA':
            __block_result_3__ = ta.sma(source, length)
        elif __switch__ == 'RMA':
            __block_result_3__ = ta.rma(source, length)
        elif __switch__ == 'WMA':
            __block_result_3__ = ta.wma(source, length)
        else:
            __block_result_3__ = na
        ema = __block_result_3__
        return ema

    @export
    def taGetVwap(src: float, anchor: str, multiplier: float):
        __block_result_4__ = na
        __switch__ = anchor
        if __switch__ == 'Session':
            __block_result_4__ = ta.change(time('D'))
        elif __switch__ == 'Week':
            __block_result_4__ = ta.change(time('W'))
        elif __switch__ == 'Month':
            __block_result_4__ = ta.change(time('M'))
        elif __switch__ == 'Quarter':
            __block_result_4__ = ta.change(time('3M'))
        elif __switch__ == 'Year':
            __block_result_4__ = ta.change(time('12M'))
        else:
            __block_result_4__ = False
        isNewPeriod = __block_result_4__
        sumSrcVol: PersistentSeries[float] = na(float)
        sumVol: PersistentSeries[float] = na(float)
        sumSrcSrcVol: PersistentSeries[float] = na(float)
        sumSrcVol = src * volume if isNewPeriod else src * volume + sumSrcVol[1]
        sumVol = volume if isNewPeriod else volume + sumVol[1]
        sumSrcSrcVol = volume * math.pow(src, 2) if isNewPeriod else volume * math.pow(src, 2) + sumSrcSrcVol[1]
        vwap = sumSrcVol / sumVol
        variance = sumSrcSrcVol / sumVol - math.pow(vwap, 2)
        variance = 0 if variance < 0 else variance
        standardDeviation = math.sqrt(variance)
        lowerBandValue = vwap - standardDeviation * multiplier
        upperBandValue = vwap + standardDeviation * multiplier
        return (vwap, lowerBandValue, upperBandValue)

    @export
    def taGetExtremes(value: Series[float], direction: str, lookbackPeriod: int, sampleSize: int):
        extremes: list[float] = array.new_float()
        for i in pine_range(0, lookbackPeriod - 1, 1):
            array.push(extremes, value[i])
        topExtremes: list[float] = array.new_float()
        for i in pine_range(0, sampleSize - 1, 1):
            etremeAtN: float = na(float)
            if direction == 'high':
                etremeAtN = array.get(extremes, array.indexof(extremes, array.max(extremes, i)))
            else:
                if direction == 'low':
                    etremeAtN = array.get(extremes, array.indexof(extremes, array.min(extremes, i)))
                else:
                    runtime.error("You must slect either 'high' or 'low' for the 'direction' when using taGetExtremes.")
            array.push(topExtremes, etremeAtN)
        minExtreme = array.min(topExtremes)
        avgExtreme = array.avg(topExtremes)
        maxExtreme = array.max(topExtremes)
        return (minExtreme, avgExtreme, maxExtreme)

    @export
    def taGetSupport(lookback: int, lookahead: int):
        support = fixnan(inline_series(ta.pivotlow(lookback, lookahead), 1))
        return support

    @export
    def taGetResistance(lookback: int, lookahead: int):
        resistance = fixnan(inline_series(ta.pivothigh(lookback, lookahead), 1))
        return resistance

    @export
    def taGetPercentDif(number1: float, number2: float):
        difRaw = number1 - number2
        dif = difRaw * -1 if difRaw < 0 else difRaw
        avg = (number1 + number2) / 2
        percentDif = dif / avg * 100
        return percentDif

    @export
    def isBetweenTwoTimes(session__ren__: str, timezone: str):
        return na(time(timeframe.period, session__ren__, timezone)) == False

    @export
    def getAllTradeIDs():
        closed_orders: list[str] = array.new_string()
        open_orders: list[str] = array.new_string()
        all_orders: list[str] = array.new_string()
        currentlyInAPosition = strategy.position_size != 0
        open_order_count = strategy.opentrades - 1
        __loop_0__ = pine_loop(0, 1)
        while __loop_0__.step(strategy.closedtrades):
            i = __loop_0__.value
            id = strategy.closedtrades.entry_id(i)
            array.push(closed_orders, id)
        if currentlyInAPosition:
            for i in pine_range(0, open_order_count, 1):
                id = strategy.opentrades.entry_id(i)
                array.push(open_orders, id)
        array.concat(all_orders, closed_orders)
        array.concat(all_orders, open_orders)
        return all_orders

    @export
    def getClosedTradeSince(barNumberToCompare: int):
        closedOrderBarNumbers: list[int] = array.new_int()
        closedOrderPrices: list[int] = array.new_int()
        __loop_0__ = pine_loop(0, 1)
        while __loop_0__.step(strategy.closedtrades - 1):
            i = __loop_0__.value
            bar = strategy.closedtrades.exit_bar_index(i)
            price = strategy.closedtrades.exit_price(i)
            if bar > barNumberToCompare:
                array.push(closedOrderBarNumbers, bar)
                array.push(closedOrderPrices, bar)
        return (closedOrderBarNumbers, closedOrderPrices)

    @export
    def getCountOfClosedTradeSince(barNumberToCompare: int):
        count: int = 0
        if strategy.position_size != 0:
            __loop_1__ = pine_loop(0, 1)
            while __loop_1__.step(strategy.closedtrades - 1):
                i = __loop_1__.value
                bar = strategy.closedtrades.exit_bar_index(i)
                if bar > barNumberToCompare:
                    count = count + 1
        else:
            count = count + 0
        return count

    @export
    def orderAlreadyClosedSince(exitId: str, barNumberToCompare: int):
        closedOrderIds: list[str] = array.new_string()
        currentlyInAPosition = strategy.position_size != 0
        __block_result_5__ = na
        if currentlyInAPosition:
            __loop_1__ = pine_loop(0, 1)
            while __loop_1__.step(strategy.closedtrades - 1):
                i = __loop_1__.value
                bar = strategy.closedtrades.exit_bar_index(i)
                price = strategy.closedtrades.exit_price(i)
                id = strategy.closedtrades.exit_id(i)
                if bar > barNumberToCompare:
                    array.push(closedOrderIds, id)
            alreadyClosed = array.includes(closedOrderIds, exitId)
            __block_result_5__ = alreadyClosed
        return __block_result_5__

    @export
    def getOpenTradeIDs():
        open_orders: list[str] = array.new_string()
        open_order_count = strategy.opentrades
        if open_order_count > 0:
            for i in pine_range(0, open_order_count - 1, 1):
                id = strategy.opentrades.entry_id(i)
                array.push(open_orders, id)
        return open_orders

    @export
    def orderAlreadyExists(order_id: str):
        return True if array.includes(getAllTradeIDs(), order_id) else False

    @export
    def orderCurrentlyExists(order_id: str):
        return True if array.includes(getOpenTradeIDs(), order_id) else False

    @export
    def getLockedLadderStart(startingLadderPrice: float):
        ladderInStart: Persistent[float] = startingLadderPrice
        ladderInActive: Persistent[bool] = False
        firstLadderOpenedOnBar: Persistent[int] = 0
        currentlyInAPosition: bool = strategy.position_size != 0
        if currentlyInAPosition and (not ladderInActive):
            ladderInStart = strategy.opentrades.entry_price(0)
            firstLadderOpenedOnBar = strategy.opentrades.entry_bar_index(0)
            ladderInActive = True
        else:
            if not currentlyInAPosition:
                ladderInStart = startingLadderPrice
                firstLadderOpenedOnBar = 0
                ladderInActive = False
        return (ladderInStart, firstLadderOpenedOnBar)

    @export
    def getAveragePriceOfFilledLadders():
        avgPrice: Persistent[float] = na(float)
        mostOpenTradesSinceFirstLadderFilled: Persistent[int] = 0
        currentlyInAPosition: bool = strategy.position_size != 0
        if currentlyInAPosition and strategy.opentrades > mostOpenTradesSinceFirstLadderFilled:
            mostOpenTradesSinceFirstLadderFilled = strategy.opentrades
            avgPrice = strategy.position_avg_price
        else:
            if not currentlyInAPosition:
                mostOpenTradesSinceFirstLadderFilled = 0
                avgPrice = na
        return avgPrice

    @export
    def getContractCount(amount: str, price: float):
        contractCount: float = 0.0
        accountBalance = strategy.equity
        if string.contains(amount, '%a') and accountBalance > 0:
            percentAmount = string.split(amount, '%')
            contractCount = string.tonumber(array.get(percentAmount, 0)) / 100 * accountBalance / price
        else:
            contractCount = string.tonumber(amount) / price
        return contractCount

    @export
    def getLadderInSteps(side: str, amount: float, amountType: str, ladderRungs: int, ladderStart: float, ladderStop: float, stepSpacingPercent: float, roundTo: int):
        entryPrices: list[float] = array.new_float()
        contractCounts: list[float] = array.new_float()
        entryAmounts: list[float] = array.new_float()
        orderNames: list[str] = array.new_string()
        ladderSpacing: float = na(float)
        contractCount: float = na(float)
        entryAmount: float = na(float)
        if ladderStart and ladderStop and (not stepSpacingPercent):
            ladderSpacing = (ladderStart - ladderStop) / ladderRungs
        else:
            ladderSpacing = ladderStart * (stepSpacingPercent / 100)
        if ladderStart and ladderSpacing:
            for i in pine_range(0, ladderRungs - 1, 1):
                price = ladderStart - ladderSpacing * i if side == 'buy' else ladderStart + ladderSpacing * i
                orderName = 'Long - ' + string.tostring(i + 1) if side == 'buy' else 'Short - ' + string.tostring(i + 1)
                if amountType == 'Percent Of Account':
                    contractCount = math.round(amount / 100 * strategy.equity / price, roundTo)
                    entryAmount = math.round(amount, roundTo)
                if amountType == 'Dollars':
                    contractCount = math.round(amount / price, roundTo)
                    entryAmount = math.round(amount, roundTo)
                if amountType == 'Contracts':
                    contractCount = math.round(amount, roundTo)
                    entryAmount = math.round(amount, roundTo)
                array.push(entryPrices, price)
                array.push(contractCounts, contractCount)
                array.push(entryAmounts, entryAmount)
                array.push(orderNames, orderName)
        return (entryPrices, contractCounts, entryAmounts, orderNames)

    @export
    def getLadderOutSteps(side: str, ladderStart: float, ladderRungs: int, stepSpacingPercent: float, roundTo: int):
        prices: list[float] = array.new_float()
        quantityPercents: list[float] = array.new_float()
        orderNames: list[str] = array.new_string()
        ladderSpacing: float = ladderStart * (stepSpacingPercent / 100)
        quantityPercent: int = math.floor(100 / ladderRungs)
        remainingPercent: int = 100
        percentToClose: int = na(int)
        for i in pine_range(0, ladderRungs - 1, 1):
            price = math.round(ladderStart + ladderSpacing * i if side == 'sell' else ladderStart - ladderSpacing * i, roundTo)
            orderName = 'Ladder Out - ' + string.tostring(i + 1)
            if i == ladderRungs - 1:
                percentToClose = remainingPercent
            else:
                percentToClose = quantityPercent
                remainingPercent = remainingPercent - percentToClose
            array.push(prices, price)
            array.push(quantityPercents, percentToClose)
            array.push(orderNames, orderName)
        return (prices, quantityPercents, orderNames)

    @export
    def getRateOfChange(source: Series[float], length: int):
        rateOfChange: float = 100 * (source - source[length]) / source[length]
        return rateOfChange

    @export
    def closeUnfilledEntriesAfter(cancelUnfilledOrdersAfter: int, cancelUnfilledOrdersType: str, startingBar: int):
        chartTimeframeMinutes: int = timeframe.in_seconds(timeframe.period) / 60
        currentlyInAPosition: bool = strategy.position_size != 0
        cancelUnfilledEntries: bool = False
        numberOfClosedTrades: int = getCountOfClosedTradeSince(startingBar)
        cancelOnBar: int = na(int)
        if currentlyInAPosition:
            __block_result_6__ = na
            __switch_1__ = cancelUnfilledOrdersType
            if __switch_1__ == 'exits':
                __block_result_6__ = numberOfClosedTrades >= cancelUnfilledOrdersAfter
            elif __switch_1__ == 'bars':
                __block_result_6__ = bar_index >= startingBar + cancelUnfilledOrdersAfter
            elif __switch_1__ == 'days':
                __block_result_6__ = bar_index >= startingBar + cancelUnfilledOrdersAfter * 1440 / chartTimeframeMinutes
            elif __switch_1__ == 'hours':
                __block_result_6__ = bar_index >= startingBar + cancelUnfilledOrdersAfter * 60 / chartTimeframeMinutes
            elif __switch_1__ == 'minutes':
                __block_result_6__ = bar_index >= startingBar + cancelUnfilledOrdersAfter / chartTimeframeMinutes
            cancelUnfilledEntries = __block_result_6__
            __block_result_7__ = na
            __switch_1__ = cancelUnfilledOrdersType
            if __switch_1__ == 'exits':
                __block_result_7__ = strategy.closedtrades.exit_bar_index(0) if numberOfClosedTrades >= cancelUnfilledOrdersAfter else na
            elif __switch_1__ == 'bars':
                __block_result_7__ = startingBar + cancelUnfilledOrdersAfter
            elif __switch_1__ == 'days':
                __block_result_7__ = startingBar + cancelUnfilledOrdersAfter * 1440 / chartTimeframeMinutes
            elif __switch_1__ == 'hours':
                __block_result_7__ = startingBar + cancelUnfilledOrdersAfter * 60 / chartTimeframeMinutes
            elif __switch_1__ == 'minutes':
                __block_result_7__ = startingBar + cancelUnfilledOrdersAfter / chartTimeframeMinutes
            cancelOnBar = __block_result_7__
        else:
            cancelUnfilledEntries = False
            cancelOnBar = na
        return (cancelUnfilledEntries, cancelOnBar)

    @export
    def getEntryNames(numberOfEntries: int, side: str):
        entryNamesArray: list[str] = array.new_string(numberOfEntries)
        for i in pine_range(0, numberOfEntries - 1, 1):
            entryName = 'Long - ' + string.tostring(i + 1) if side == 'buy' else 'Short - ' + string.tostring(i + 1)
            array.insert(entryNamesArray, i, entryName)
            array.from_items('Long' + ' - 1' if side == 'buy' else 'Short' + ' - 1', 'Long' + ' - 2' if side == 'buy' else 'Short' + ' - 2', 'Long' + ' - 3' if side == 'buy' else 'Short' + ' - 3', 'Long' + ' - 4' if side == 'buy' else 'Short' + ' - 4', 'Long' + ' - 5' if side == 'buy' else 'Short' + ' - 5', 'Long' + ' - 6' if side == 'buy' else 'Short' + ' - 6')
        return entryNamesArray

    @export
    def formatEntryPrices(entryPrices: str):
        entryPricesArray = string.split(entryPrices, ',')
        entryPricesString: str = na(str)
        for i in pine_range(0, array.size(entryPricesArray) - 1, 1):
            entryPricesString = entryPricesString + string.format('{0,number,currency}', array.get(entryPricesArray, i))
            if i != array.size(entryPricesArray) - 1:
                entryPricesString = entryPricesString + ','
        return entryPricesString

    def getProfitTargetAmount(amount: str):
        profitTargetAmount: str = na(str)
        if string.contains(amount, '%'):
            profitTargetAmount = amount + 'p'
        else:
            runtime.error("The profit target amount must be represented as a % of the position. Update 'profitTargetAmounts' to be a CSV string of percentages like '3%, 4%, 5%'")
        return profitTargetAmount

    def getProfitTarget(target: str, symbolMaxDecimals: int):
        profitTarget: str = na(str)
        if string.contains(target, '$'):
            targetSplit = string.split(target, '$')
            roundedPrice = math.round(string.tonumber(array.get(targetSplit, 1)), symbolMaxDecimals)
            profitTarget = '@' + string.tostring(roundedPrice)
        else:
            if string.contains(target, '%'):
                profitTarget = target + 'p'
            else:
                runtime.error("The profit target must be represented as a % or price. Update 'profitTargets' to be a CSV string of percentages like '3%, 4%, 5%' or prices like '$20000.00, 21000.00, 22000.00'")
        return profitTarget

    def getEntryPrices(array__ren__: list[float], roundTo: int):
        roundedArray: list[str] = array.new_string(0)
        for i in pine_range(0, array.size(array__ren__) - 1, 1):
            roundedVal = math.round(array.get(array__ren__, i), roundTo)
            array.push(roundedArray, string.tostring(roundedVal))
        return roundedArray

    @export
    def getLotSize(type: str, amount: float, leverage: float, roundTo: int):
        contractCount: float = na(float)
        entryAmount: float = na(float)
        if type == 'Percent Of Account':
            contractCount = math.round(amount / 100 * strategy.equity / close, roundTo) * leverage
            entryAmount = math.round(amount, roundTo)
        if type == 'Dollars':
            contractCount = math.round(amount / close, roundTo) * leverage
            entryAmount = math.round(amount, roundTo)
        if type == 'Contracts':
            contractCount = math.round(amount, roundTo) * leverage
            entryAmount = math.round(amount, roundTo)
        return (contractCount, entryAmount)

    @export
    def getPairOverrides(symbolOverride: str, currencyOverride: str):
        baseCurrency: str = na(str)
        symbol: str = na(str)
        if currencyOverride != '':
            baseCurrency = currencyOverride
        else:
            baseCurrency = getBaseCurrency()
        if symbolOverride != '':
            symbol = symbolOverride
        else:
            symbol = getChartSymbol()
        return (symbol, baseCurrency)

    def getEntryQuantity(entryAmount: float, type: str, price: float, roundTo: int, leverage: float):
        entryQuantity: str = na(str)
        leveragedPercentAmount: float = na(float)
        if type == 'Contracts':
            entryQuantity = string.tostring(math.round(entryAmount, roundTo))
        else:
            if type == 'Percent Of Account':
                if leverage > 1:
                    leveragedPercentAmount = entryAmount * leverage
                else:
                    leveragedPercentAmount = entryAmount * leverage
                entryQuantity = string.tostring(math.round(leveragedPercentAmount, roundTo)) + '%a'
            else:
                if type == 'Dollars':
                    entryQuantity = string.tostring(math.round(entryAmount / price, roundTo))
        return entryQuantity

    def getProfitTargets(array__ren__: list[float], type: str, roundTo: int):
        inputSize: int = array.size(array__ren__) - 1
        output: list[str] = array.new_string(0)
        target: str = na(str)
        remainingPercentage: float = 100.0
        for i in pine_range(0, inputSize, 1):
            percent: float = 0.0
            lastTarget: bool = i == inputSize
            if type == 'percent':
                if lastTarget:
                    percent = remainingPercentage
                else:
                    percent = math.round(array.get(array__ren__, i), roundTo)
                    remainingPercentage = remainingPercentage - percent
                target = 'e' + string.tostring(percent) + '%'
            else:
                if type == 'price':
                    target = '@' + string.tostring(math.round(array.get(array__ren__, i), roundTo))
                else:
                    runtime.error('The "profitTargetType must be "percent" or "price".')
            array.push(output, target)
        return output

    def getProfitTargetAmounts(array__ren__: list[float], roundTo: int):
        output: list[str] = array.new_string(0)
        remainingPercentage: float = 100.0
        targetPercentage: float = 0.0
        for i in pine_range(0, array.size(array__ren__) - 1, 1):
            if i == array.size(array__ren__) - 1:
                targetPercentage = remainingPercentage
            else:
                targetPercentage = math.round(array.get(array__ren__, i), roundTo)
                remainingPercentage = remainingPercentage - targetPercentage
            array.push(output, string.tostring(targetPercentage) + '%p')
        return output

    def getStop(side: str, stopTriggerType: str, stopTrigger: float, stopLimitOffset: float, roundTo: int):
        stopTriggerVal: str = na(str)
        stopLimitOffsetVal: str = na(str)
        if stopTriggerType == 'percent':
            stopTriggerVal = 'e' + string.tostring(math.round(stopTrigger, roundTo)) + '%'
            stopLimitOffsetVal = 'e' + string.tostring(math.round(stopTrigger - stopTrigger * (stopLimitOffset / 100) if side == 'buy' else stopTrigger + stopTrigger * (stopLimitOffset / 100), roundTo)) + '%'
        if stopTriggerType == 'price':
            stopTriggerVal = '@' + string.tostring(math.round(stopTrigger, roundTo))
            stopLimitOffsetVal = '@' + string.tostring(math.round(stopTrigger - stopTrigger * (stopLimitOffset / 100) if side == 'buy' else stopTrigger + stopTrigger * (stopLimitOffset / 100), roundTo))
        return (stopTriggerVal, stopLimitOffsetVal)

    def getProfit(side: str, profitTriggerType: str, profitTrigger: float, profitLimitOffset: float, roundTo: int):
        profitTriggerVal: str = na(str)
        profitLimitOffsetVal: str = na(str)
        if profitTriggerType == 'percent':
            profitTriggerVal = 'e' + string.tostring(math.round(profitTrigger, roundTo)) + '%'
            profitLimitOffsetVal = 'e' + string.tostring(math.round(profitTrigger - profitTrigger * (profitLimitOffset / 100) if side == 'buy' else profitTrigger + profitTrigger * (profitLimitOffset / 100), roundTo)) + '%'
        if profitTriggerType == 'price':
            profitTriggerVal = '@' + string.tostring(math.round(profitTrigger, roundTo))
            profitLimitOffsetVal = '@' + string.tostring(math.round(profitTrigger - profitTrigger * (profitLimitOffset / 100) if side == 'buy' else profitTrigger + profitTrigger * (profitLimitOffset / 100), roundTo))
        return (profitTriggerVal, profitLimitOffsetVal)

    @export
    def getAlertatrongAlertMessages(tag: str, secret: str, symbol: str, baseCurrency: str, pairDivider: str, side: str, symbolMaxDecimals: int, leverage: int, leverageType: str, entryPrices: list[float], entryAmounts: list[float], entryAmountType: str, profitTargets: list[float], profitTargetType: str, profitTargetAmounts: list[float], stopTrigger: float, stopTriggerType: str, stopLimitOffset: float, trailingStopTrigger: float, trailingStopTriggerType: str, trailingStopLimitOffset: float):
        closeSide = 'sell' if side == 'buy' else 'buy'
        initializeOrder = secret + '(' + symbol + pairDivider + baseCurrency + ') {' + '\n'
        messageEnd: str = '} #bot'
        entryPricesFormatted = getEntryPrices(array__ren__=entryPrices, roundTo=symbolMaxDecimals)
        profitTargetsFormatted = getProfitTargets(array__ren__=profitTargets, type=profitTargetType, roundTo=symbolMaxDecimals)
        profitTargetAmountsFormatted = getProfitTargetAmounts(array__ren__=profitTargetAmounts, roundTo=symbolMaxDecimals)
        stopTriggerFormatted, stopTriggerOffestFormatted = getStop(closeSide, stopTriggerType, stopTrigger, stopLimitOffset, roundTo=symbolMaxDecimals)
        settingsLeverageType = 'exchangeSettings(leverage=' + string.lower(leverageType) + ');' + '\n'
        settingsLeverageAmount = 'exchangeSettings(leverage=' + string.tostring(leverage) + '); ' + '\n'
        entryOrders: list[str] = array.new_string(0)
        for i in pine_range(0, array.size(entryPricesFormatted) - 1, 1):
            waitingLimit = 'waitingLimit(side=' + side + ', amount=' + getEntryQuantity(entryAmount=array.get(entryAmounts, i), type=entryAmountType, price=array.get(entryPrices, i), leverage=leverage, roundTo=symbolMaxDecimals) + ', offset=@' + array.get(entryPricesFormatted, i) + ', tag=' + tag + '-entry);' + '\n'
            profitTargets__00000236__: str = ''
            for x in pine_range(0, array.size(profitTargetsFormatted) - 1, 1):
                profitTarget = 'limit(side=' + closeSide + ', amount=' + array.get(profitTargetAmountsFormatted, x) + ', offset=' + array.get(profitTargetsFormatted, x) + ', reduceOnly=true, tag=' + tag + ');' + '\n'
                profitTargets__00000236__ = profitTargets__00000236__ + profitTarget
            stopOrder = 'stopOrder(side=' + closeSide + ', amount=100%p, offset=' + stopTriggerFormatted + ', limitOffset=' + stopTriggerOffestFormatted + ', trigger=last, reduceOnly=true, tag=' + tag + ');' + '\n'
            entryOrder = initializeOrder + settingsLeverageType + settingsLeverageAmount + waitingLimit + profitTargets__00000236__ + stopOrder + messageEnd
            array.push(entryOrders, entryOrder)
        cancelUnfilledEntries = 'cancel(which=tagged, tag=' + tag + '-entry);' + '\n'
        cancelEverythingElse = 'cancel(which=tagged, tag=' + tag + ');' + '\n'
        cancelEntriesMessage = initializeOrder + cancelUnfilledEntries + messageEnd
        trailingStopTriggerFormatted, trailingStopTriggerOffestFormatted = getStop(side=closeSide, stopTriggerType=trailingStopTriggerType, stopTrigger=trailingStopTrigger, stopLimitOffset=trailingStopLimitOffset, roundTo=symbolMaxDecimals)
        trailingStop = 'trailingStop(side=' + closeSide + ', amount=100%p, offset=' + trailingStopTriggerFormatted + ', limitOffset=' + trailingStopTriggerOffestFormatted + ', trigger=last, trailingMethod=continuous, reduceOnly=true, tag=' + tag + ');' + '\n'
        trailingStopMessage = initializeOrder + cancelUnfilledEntries + cancelEverythingElse + trailingStop + messageEnd
        return (entryOrders, cancelEntriesMessage, trailingStopMessage)

    @export
    def getAlertatronMarketEntryMessage(secret: str, symbol: str, baseCurrency: str, pairDivider: str, side: str, symbolMaxDecimals: int, leverage: int, leverageType: str, entryPrice: float, amount: float, amountType: str, stopTrigger: float, stopTriggerType: str, stopLimitOffset: float):
        closeSide = 'sell' if side == 'buy' else 'buy'
        qty = getEntryQuantity(entryAmount=amount, type=amountType, leverage=leverage, price=entryPrice, roundTo=symbolMaxDecimals)
        stopTriggerFormatted, stopTriggerOffestFormatted = getStop(closeSide, stopTriggerType, stopTrigger, stopLimitOffset, roundTo=symbolMaxDecimals)
        tradePair = symbol + pairDivider + baseCurrency
        initializeOrder = secret + '(' + tradePair + ') {' + '\n'
        settingsLeverageType = 'exchangeSettings(leverage=' + string.lower(leverageType) + ');' + '\n'
        settingsLeverageAmount = 'exchangeSettings(leverage=' + string.tostring(leverage) + '); ' + '\n'
        cancelExistingOrders = 'cancel(which=tagged, tag=' + tradePair + ');' + '\n'
        market = 'market(side=' + side + ', amount=' + qty + ', tag=' + tradePair + ');' + '\n'
        stopOrder = 'stopOrder(side=' + closeSide + ', amount=100%p, offset=' + stopTriggerFormatted + ', limitOffset=' + stopTriggerOffestFormatted + ', trigger=last, reduceOnly=true);' + '\n'
        messageEnd: str = '} #bot'
        marketEntryMessage = initializeOrder + settingsLeverageType + settingsLeverageAmount + cancelExistingOrders + market + stopOrder + messageEnd
        return marketEntryMessage

    @export
    def getAlertatronOcoMessage(secret: str, symbol: str, baseCurrency: str, pairDivider: str, side: str, symbolMaxDecimals: int, leverage: int, leverageType: str, entryPrice: float, amount: float, amountType: str, stopTrigger: float, stopTriggerType: str, stopLimitOffset: float, profitTrigger: float, profitTriggerType: str, profitLimitOffset: float):
        closeSide = 'sell' if side == 'buy' else 'buy'
        qty = getEntryQuantity(entryAmount=amount, type=amountType, leverage=leverage, price=entryPrice, roundTo=symbolMaxDecimals)
        stopTriggerFormatted, stopTriggerOffestFormatted = getStop(closeSide, stopTriggerType, stopTrigger, stopLimitOffset, roundTo=symbolMaxDecimals)
        profitTargetFormatted, profitTriggerOffsetFormatted = getProfit(closeSide, profitTriggerType, profitTrigger, profitLimitOffset, roundTo=symbolMaxDecimals)
        tradePair = symbol + pairDivider + baseCurrency
        initializeOrder = secret + '(' + tradePair + ') {' + '\n'
        settingsLeverageType = 'exchangeSettings(leverage=' + string.lower(leverageType) + ');' + '\n'
        settingsLeverageAmount = 'exchangeSettings(leverage=' + string.tostring(leverage) + '); ' + '\n'
        cancelExistingOrders = 'cancel(which=tagged, tag=' + tradePair + ');' + '\n'
        market = 'market(side=' + side + ', amount=' + qty + ', tag=' + tradePair + ');' + '\n'
        stopOrder = 'stopOrder(side=' + closeSide + ', amount=100%p, offset=' + stopTriggerFormatted + ', limitOffset=' + stopTriggerOffestFormatted + ', trigger=last, reduceOnly=true);' + '\n'
        profitOrder = 'stopOrder(side=' + closeSide + ', amount=100%p, offset=' + profitTargetFormatted + ', limitOffset=' + profitTriggerOffsetFormatted + ', trigger=last, reduceOnly=true);' + '\n'
        messageEnd: str = '} #bot'
        marketEntryMessage = initializeOrder + settingsLeverageType + settingsLeverageAmount + cancelExistingOrders + market + stopOrder + profitOrder + messageEnd
        return marketEntryMessage

    @export
    def getAlertatronMarketExitMessage(secret: str, symbol: str, baseCurrency: str, pairDivider: str, side: str):
        initializeOrder = secret + '(' + symbol + pairDivider + baseCurrency + ') {' + '\n'
        cancelExistingOrders = 'cancel(which=all);' + '\n'
        market = 'market(side=' + side + ', amount=100%p, reduceOnly=true);' + '\n'
        messageEnd: str = '} #bot'
        marketExitMessage = initializeOrder + cancelExistingOrders + market + messageEnd
        return marketExitMessage

    @export
    def getAlertatronAlertMessageMarketClosePercentOfPosition(secret: str, symbol: str, baseCurrency: str, pairDivider: str, percent: int, side: str):
        initializeOrder = secret + '(' + symbol + pairDivider + baseCurrency + ') {' + '\n'
        cancelExistingOrders = 'cancel(which=all);' + '\n'
        market = 'market(side=' + side + ', amount=' + string.tostring(percent) + '%p, reduceOnly=true);' + '\n'
        messageEnd: str = '} #bot'
        marketExitMessage = initializeOrder + cancelExistingOrders + market + messageEnd
        return marketExitMessage

    @export
    def convertTimeframeToString(timeframe__ren__: str):
        timeToConvert: str = na(str)
        if timeframe__ren__ == timeframe.period:
            timeToConvert = timeframe.period
        else:
            timeToConvert = timeframe__ren__
        __block_result_8__ = na
        __switch__ = timeToConvert
        if __switch__ == '1':
            __block_result_8__ = '1m'
        elif __switch__ == '3':
            __block_result_8__ = '3m'
        elif __switch__ == '5':
            __block_result_8__ = '5m'
        elif __switch__ == '15':
            __block_result_8__ = '15m'
        elif __switch__ == '30':
            __block_result_8__ = '30m'
        elif __switch__ == '45':
            __block_result_8__ = '45m'
        elif __switch__ == '60':
            __block_result_8__ = '1h'
        elif __switch__ == '120':
            __block_result_8__ = '2h'
        elif __switch__ == '180':
            __block_result_8__ = '3h'
        elif __switch__ == '240':
            __block_result_8__ = '4h'
        elif __switch__ == '720':
            __block_result_8__ = '12h'
        elif __switch__ == '1D':
            __block_result_8__ = '1D'
        elif __switch__ == '3D':
            __block_result_8__ = '3D'
        elif __switch__ == '1W':
            __block_result_8__ = '1W'
        elif __switch__ == '1M':
            __block_result_8__ = '1M'
        elif __switch__ == '6M':
            __block_result_8__ = '6M'
        printTime = __block_result_8__
        return printTime


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
