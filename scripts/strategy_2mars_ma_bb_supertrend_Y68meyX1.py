"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_loop
from pynecore.core.pine_cast import cast_int
from pynecore.lib import (
    close, color, currency, display, fill, high, input, low, math, na, nz,
    open, plot, position, script, strategy, string, syminfo, ta, table, text
)
from pynecore.types import Color, Persistent, Series, Table
import lib.facejungle.utils.v17 as utils

GENERAL_GRP: str = 'General'
ST_GRP: str = 'SuperTrend'
MA_GRP: str = 'Moving average'
BB_GRP: str = 'Bollinger Bands'
TP_GRP: str = 'Take-Profit'
LO_GRP: str = 'Limit-Orders'
SL_GRP: str = 'Stop-Loss'


@script.strategy('2Mars - MA / BB / SuperTrend', shorttitle='2Mars', overlay=True, initial_capital=10000, pyramiding=3, currency=currency.USD, default_qty_type=strategy.percent_of_equity, default_qty_value=5, commission_type=strategy.commission.percent, commission_value=0.1, margin_long=100.0, margin_short=100.0, max_bars_back=5000, calc_on_order_fills=False, calc_on_every_tick=False, process_orders_on_close=True, use_bar_magnifier=False, close_by_id=True)
def main(
    priceSource: Series[float] = input.source(close, 'Source', group=GENERAL_GRP, display=display.none),
    barsConfirm=input.int(2, 'Bars confirm', minval=1, step=1, display=display.none, group=GENERAL_GRP),
    entryTrigger=input.string('close', 'Entry trigger', options=('close', 'high/low', 'high/low median', 'open/close median'), group=GENERAL_GRP, display=display.none),
    useSuperTrendSignal=input.bool(False, title='SuperTrend as entry signal', tooltip='Not a required! Uses for additional entry to position. For entry will required confirm MA trend', display=display.none, group=ST_GRP),
    useSuperTrend=input.bool(True, title='SuperTrend confirm', tooltip='Not a required! Uses for - Confirm entry to position. Stop-loss confirm. Stop-loss price.', display=display.none, group=ST_GRP),
    superTrendFactor=input.float(4, title='Factor', step=0.1, display=display.none, group=ST_GRP),
    superTrendPeriod=input.int(20, title='Length', display=display.none, group=ST_GRP),
    useMaStrategy=input.bool(True, title='Use MA Cross strategy', tooltip='Not a required! Uses for - Entry signal to position when signal and basis line cross (MA Cross strategy). When price cross the MA (add. orders #3).', display=display.none, group=MA_GRP),
    maBasisType=input.string('sma', 'Basis MA type', options=('alma', 'ema', 'dema', 'tema', 'sma', 'smma', 'ssma', 'hma', 'rma', 'swma', 'vwma', 'wma', 'linreg', 'median', 'mom', 'high', 'low', 'medianHigh', 'medianLow', 'percentrank'), group=MA_GRP, display=display.none),
    maSignalType=input.string('sma', 'Signal MA type', options=('alma', 'ema', 'dema', 'tema', 'sma', 'smma', 'ssma', 'hma', 'rma', 'swma', 'vwma', 'wma', 'linreg', 'median', 'mom', 'high', 'low', 'medianHigh', 'medianLow', 'percentrank'), group=MA_GRP, display=display.none),
    maRatio=input.float(1.08, 'Ratio', minval=0.01, step=0.02, group=MA_GRP, display=display.none),
    maMultiplier=input.int(89, 'Multiplier', minval=1, step=1, group=MA_GRP, tooltip='Basis length = Ratio * Multiplier, Signal length = Multiplier', display=display.none),
    bbType=input.string('wma', 'Type', options=('alma', 'ema', 'dema', 'tema', 'sma', 'smma', 'ssma', 'hma', 'rma', 'swma', 'vwma', 'wma', 'linreg', 'median', 'mom', 'high', 'low', 'medianHigh', 'medianLow', 'percentrank'), tooltip='Not a required! Uses for - Take profit. Additionals orders #1 and #2. If use ATR stop-loss, lower and upper line #3 used for stop-loss price update.', group=BB_GRP, display=display.none),
    bbLength=input.int(30, 'length', minval=1, step=1, group=BB_GRP, display=display.none),
    bbMultiplier=input.float(3, minval=1, maxval=50, step=0.1, title='StdDev', group=BB_GRP, display=display.none),
    useBBLong=input.string('lower3', '↗️ Long orders :', options=('lower', 'lower2', 'lower3', 'upper', 'upper2', 'upper3', 'off'), inline='Short orders', display=display.none),
    useBBLong2=input.string('lower2', ' + ', options=('lower', 'lower2', 'lower3', 'upper', 'upper2', 'upper3', 'off'), inline='Short orders', display=display.none),
    useBBLong3=input.string('off', ' + ', options=('basis', 'signal', 'off'), inline='Short orders', display=display.none),
    useBBShort=input.string('upper3', '↘️ Short orders:', options=('upper', 'upper2', 'upper3', 'lower', 'lower2', 'lower3', 'off'), inline='Long orders', display=display.none),
    useBBShort2=input.string('upper2', ' + ', options=('upper', 'upper2', 'upper3', 'lower', 'lower2', 'lower3', 'off'), inline='Long orders', display=display.none),
    useBBShort3=input.string('off', ' + ', options=('basis', 'signal', 'off'), inline='Long orders', display=display.none),
    takeProfitTrigger=input.string('close', 'Take-profit trigger', options=('close', 'high/low', 'high/low median', 'open/close median'), inline='1', group=TP_GRP, display=display.none),
    takeProfitQtyType=input.string('Percentage', 'Qty type', options=('Percentage', 'Fixed'), inline='1', group=TP_GRP, display=display.none),
    useTakeProfit=input.bool(False, title='Use TP orders', display=display.none, group=TP_GRP),
    useTakeProfit2=input.bool(True, title='Use TP orders 2', display=display.none, group=TP_GRP),
    useTakeProfit3=input.bool(True, title='Use TP orders 3', display=display.none, group=TP_GRP),
    takeProfitLongQty=input.int(5, '↗️ Long qty', minval=0, maxval=100, step=2, inline='takeQty', display=display.none, group=TP_GRP),
    takeProfitShortQty=input.int(5, '↘️ Short qty', minval=0, maxval=100, step=2, inline='takeQty', display=display.none, group=TP_GRP),
    useLimitOrder=input.bool(False, title='Use limit orders', tooltip='Calculate for before each entry order. Long: low price - ATR * Multiplier, Short: high price + ATR * Multiplier', display=display.none, group=LO_GRP),
    limitOrderPeriod=input.int(12, 'Length', minval=1, step=1, tooltip='ATR', display=display.none, group=LO_GRP),
    limitOrderMultiplier=input.float(0.1, 'Multiplier', step=0.1, display=display.none, group=LO_GRP),
    stopLossTrigger=input.string('open/close median', 'Stop-loss trigger', options=('close', 'high/low', 'high/low median', 'open/close median'), group=SL_GRP, display=display.none),
    stopLossType=input.string('ATR', 'Stop-loss:', options=('off', 'SuperTrend + ATR', 'ATR', 'StdDev'), tooltip='Update with each entry order and take profit #3. SuperTrend + ATR: update with each trend change not in our favor. If use "SuperTrend confirm", then the stop loss will require confirmation trend change.', group=SL_GRP, display=display.none),
    SLAtrPeriod=input.int(12, title='Length', tooltip='ATR and StdDev', display=display.none, group=SL_GRP),
    SLAtrMultiplierLong=input.float(6, title='Long mult.', step=0.1, tooltip='ATR: low - ATR * Long mult. / SuperTrend: SuperTrend - ATR * Long mult. / StdDev: low - StdDev - ATR * Long mult.', display=display.none, group=SL_GRP),
    SLAtrMultiplierShort=input.float(4.3, title='Short mult.', step=0.1, tooltip='ATR: high + ATR * Short mult. / SuperTrend: SuperTrend + ATR * Short mult. / StdDev: high + StdDev + ATR * Short mult.', display=display.none, group=SL_GRP),
    useFlexStopLoss=input.bool(False, title='Use flex stop-loss for ATR and StdDev', tooltip='If the SuperTrend or MA trend changes not in our favor, then adjusting the stop loss.', display=display.none, group=SL_GRP),
    SLFlexMult=input.float(0, step=0.1, title='Multiplier __________________________________', tooltip='Long: stop-loss price + (ATR * Long mult.) * Multiplier. Short: stop-loss price - (ATR * Short mult.) * Multiplier.', display=display.none, group=SL_GRP)
):
    epsilon: float = syminfo.mintick
    character_count: int = cast_int(math.log10(1 / epsilon))
    priceMedianHighLow: float = (high + low) / 2
    priceMedianOpenClose: float = (open + close) / 2
    supertrendOrig, supertrendDirection = ta.supertrend(superTrendFactor, superTrendPeriod)
    supertrend: Series[float] = ta.rma(supertrendOrig, 4)
    maBasisLengh: int = math.round(maRatio * maMultiplier)
    maBasis: float = utils.maCustomseries(priceSource, maBasisType, maBasisLengh)
    maSignal: float = utils.maCustomseries(priceSource, maSignalType, maMultiplier)
    bbUpper: Series
    bbUpper2: Series
    bbUpper3: Series
    bbLower: Series
    bbLower2: Series
    bbLower3: Series
    bbMiddle, bbUpper, bbUpper2, bbUpper3, bbUpper4, bbLower, bbLower2, bbLower3, bbLower4 = utils.fj_stdev(priceSource, bbLength, bbMultiplier, bbType)
    limitOrderAtr: float = ta.atr(limitOrderPeriod)
    limitOrderPrice: Persistent[float] = na(float)
    limitOrderDirection: Persistent[str] = 'flat'
    limitOrderPriceLong: float = math.round(low - limitOrderAtr * limitOrderMultiplier, character_count) if useLimitOrder else na
    limitOrderPriceShort: float = math.round(high + limitOrderAtr * limitOrderMultiplier, character_count) if useLimitOrder else na
    stopLossAtr: float = ta.atr(SLAtrPeriod)
    stopLossStdDev: float = ta.stdev(priceSource, SLAtrPeriod)
    stopLossPriceLong: Persistent[float] = na(float)
    stopLossPriceShort: Persistent[float] = na(float)
    calcStopLossPriceLong: float = math.round(supertrend[1] - stopLossAtr * SLAtrMultiplierLong, character_count) if stopLossType == 'SuperTrend + ATR' else math.round(low - stopLossAtr * SLAtrMultiplierLong, character_count) if stopLossType == 'ATR' else math.round(low - stopLossStdDev - stopLossAtr * SLAtrMultiplierLong, character_count) if stopLossType == 'StdDev' else na
    calcStopLossPriceShort: float = math.round(supertrend[1] + stopLossAtr * SLAtrMultiplierShort, character_count) if stopLossType == 'SuperTrend + ATR' else math.round(high + stopLossAtr * SLAtrMultiplierShort, character_count) if stopLossType == 'ATR' else math.round(high + stopLossStdDev + stopLossAtr * SLAtrMultiplierShort, character_count) if stopLossType == 'StdDev' else na
    def counterEvent(enent: bool, enent2: bool):
        scount: Series[int] = 0
        scount = nz(scount[1]) + 1 if enent and enent2 else 0
        return scount

    def barCrossoverCounter(signalPrice: float, basePrice: float):
        bcond: bool = signalPrice > basePrice
        bcount: Series[int] = 0
        bcount = nz(bcount[1]) + 1 if bcond else 0
        return bcount

    def barCrossunderCounter(signalPrice: float, basePrice: float):
        scond: bool = signalPrice < basePrice
        scount: Series[int] = 0
        scount = nz(scount[1]) + 1 if scond else 0
        return scount

    entryTriggerLong: float = high if entryTrigger == 'high/low' else priceMedianHighLow if entryTrigger == 'high/low median' else priceMedianOpenClose if entryTrigger == 'open/close median' else close
    condPositionLong: bool = strategy.position_size > 0
    condSuperTrendLong: bool = supertrendDirection < 0
    condSuperTrendLongSignal: bool = barsConfirm == barCrossunderCounter(supertrendDirection, 0)
    condMaLong: bool = barsConfirm == barCrossoverCounter(maSignal, maBasis)
    condBasisLong: bool = barsConfirm == barCrossoverCounter(entryTriggerLong, maBasis)
    condSignalLong: bool = barsConfirm == barCrossoverCounter(entryTriggerLong, maSignal)
    condBBLong1: bool = barsConfirm == barCrossoverCounter(entryTriggerLong, bbLower)
    condBBLong2: bool = barsConfirm == barCrossoverCounter(entryTriggerLong, bbLower2)
    condBBLong3: bool = barsConfirm == barCrossoverCounter(entryTriggerLong, bbLower3)
    condBBLong4: bool = barsConfirm == barCrossoverCounter(entryTriggerLong, bbUpper)
    condBBLong5: bool = barsConfirm == barCrossoverCounter(entryTriggerLong, bbUpper2)
    condBBLong6: bool = barsConfirm == barCrossoverCounter(entryTriggerLong, bbUpper3)
    entryTriggerShort: float = low if entryTrigger == 'high/low' else priceMedianHighLow if entryTrigger == 'high/low median' else priceMedianOpenClose if entryTrigger == 'open/close median' else close
    condPositionShort: bool = strategy.position_size < 0
    condSuperTrendShort: bool = supertrendDirection > 0
    condSuperTrendShortSignal: bool = barsConfirm == barCrossoverCounter(supertrendDirection, 0)
    condMaShort: bool = barsConfirm == barCrossunderCounter(maSignal, maBasis)
    condBasisShort: bool = barsConfirm == barCrossunderCounter(entryTriggerShort, maBasis)
    condSignalShort: bool = barsConfirm == barCrossunderCounter(entryTriggerShort, maSignal)
    condBBShort1: bool = barsConfirm == barCrossunderCounter(entryTriggerShort, bbUpper)
    condBBShort2: bool = barsConfirm == barCrossunderCounter(entryTriggerShort, bbUpper2)
    condBBShort3: bool = barsConfirm == barCrossunderCounter(entryTriggerShort, bbUpper3)
    condBBShort4: bool = barsConfirm == barCrossunderCounter(entryTriggerShort, bbLower)
    condBBShort6: bool = barsConfirm == barCrossunderCounter(entryTriggerShort, bbLower3)
    condBBShort5: bool = barsConfirm == barCrossunderCounter(entryTriggerShort, bbLower2)
    def stopLossShort(orderComment: str = na):
        strategy.cancel('Short')
        return strategy.close('Short', qty_percent=100, comment=orderComment if na(orderComment) == False else na)

    def stopLossLong(orderComment: str = na):
        strategy.cancel('Long')
        return strategy.close('Long', qty_percent=100, comment=orderComment if na(orderComment) == False else na)

    def newEntryLong(orderComment: str = na):
        if condPositionShort:
            stopLossShort('Close short')
        return strategy.entry('Long', strategy.long, stop=stopLossPriceLong if stopLossType != 'off' else na, limit=limitOrderPriceLong if useLimitOrder else na, comment=orderComment if na(orderComment) == False else na)

    def newEntryShort(orderComment: str = na):
        if condPositionLong:
            stopLossLong('Close short')
        return strategy.entry('Short', strategy.short, stop=stopLossPriceShort if stopLossType != 'off' else na, limit=limitOrderPriceShort if useLimitOrder else na, comment=orderComment if na(orderComment) == False else na)

    def takeLong(orderComment: str = na):
        return strategy.close('Long', qty_percent=takeProfitLongQty if takeProfitQtyType == 'Percentage' else na, qty=takeProfitLongQty if takeProfitQtyType != 'Percentage' else na, comment=orderComment if na(orderComment) == False else na)

    def takeShort(orderComment: str = na):
        return strategy.close('Short', qty_percent=takeProfitLongQty if takeProfitQtyType == 'Percentage' else na, qty=takeProfitLongQty if takeProfitQtyType != 'Percentage' else na, comment=orderComment if na(orderComment) == False else na)

    if useSuperTrendSignal:
        if condSuperTrendLongSignal and maSignal > maBasis:
            limitOrderPrice = limitOrderPriceLong
            limitOrderDirection = 'Long'
            stopLossPriceLong = calcStopLossPriceLong
            newEntryLong(orderComment=utils.commentOrderCustomseries('enter_long', 'supertrend'))
        if condSuperTrendShortSignal and maSignal < maBasis:
            limitOrderPrice = limitOrderPriceShort
            limitOrderDirection = 'Short'
            stopLossPriceShort = calcStopLossPriceShort
            newEntryShort(orderComment=utils.commentOrderCustomseries('enter_short', 'supertrend'))
    if useSuperTrend:
        if useBBLong == 'lower' or useBBLong2 == 'lower':
            if condBBLong1 and condSuperTrendLong:
                limitOrderPrice = limitOrderPriceLong
                limitOrderDirection = 'Long'
                stopLossPriceLong = calcStopLossPriceLong
                newEntryLong(orderComment=utils.commentOrderCustomseries('enter_long', 'bbLower'))
        if useBBLong == 'lower2' or useBBLong2 == 'lower2':
            if condBBLong2 and condSuperTrendLong:
                limitOrderPrice = limitOrderPriceLong
                limitOrderDirection = 'Long'
                stopLossPriceLong = calcStopLossPriceLong
                newEntryLong(orderComment=utils.commentOrderCustomseries('enter_long', 'bbLower2'))
        if useBBLong == 'lower3' or useBBLong2 == 'lower3':
            if condBBLong3 and condSuperTrendLong:
                limitOrderPrice = limitOrderPriceLong
                limitOrderDirection = 'Long'
                stopLossPriceLong = calcStopLossPriceLong
                newEntryLong(orderComment=utils.commentOrderCustomseries('enter_long', 'bbLower3'))
        if useBBLong == 'upper' or useBBLong2 == 'upper':
            if condBBLong4 and condSuperTrendLong:
                limitOrderPrice = limitOrderPriceLong
                limitOrderDirection = 'Long'
                stopLossPriceLong = calcStopLossPriceLong
                newEntryLong(orderComment=utils.commentOrderCustomseries('enter_long', 'bbUpper'))
        if useBBLong == 'upper2' or useBBLong2 == 'upper2':
            if condBBLong5 and condSuperTrendLong:
                limitOrderPrice = limitOrderPriceLong
                limitOrderDirection = 'Long'
                stopLossPriceLong = calcStopLossPriceLong
                newEntryLong(orderComment=utils.commentOrderCustomseries('enter_long', 'bbUpper2'))
        if useBBLong == 'upper3' or useBBLong2 == 'upper3':
            if condBBLong6 and condSuperTrendLong:
                limitOrderPrice = limitOrderPriceLong
                limitOrderDirection = 'Long'
                stopLossPriceLong = calcStopLossPriceLong
                newEntryLong(orderComment=utils.commentOrderCustomseries('enter_long', 'bbUpper3'))
        if useBBLong3 == 'basis':
            if condBasisLong and condSuperTrendLong:
                limitOrderPrice = limitOrderPriceLong
                limitOrderDirection = 'Long'
                stopLossPriceLong = calcStopLossPriceLong
                newEntryLong(orderComment=utils.commentOrderCustomseries('enter_long', 'maBasis'))
        if useBBLong3 == 'signal':
            if condSignalLong and condSuperTrendLong:
                limitOrderPrice = limitOrderPriceLong
                limitOrderDirection = 'Long'
                stopLossPriceLong = calcStopLossPriceLong
                newEntryLong(orderComment=utils.commentOrderCustomseries('enter_long', 'maSignal'))
        if useMaStrategy and condSuperTrendLong and condMaLong:
            limitOrderPrice = limitOrderPriceLong
            limitOrderDirection = 'Long'
            stopLossPriceLong = calcStopLossPriceLong
            newEntryLong(orderComment=utils.commentOrderCustomseries('enter_long', 'maCross'))
        if useBBShort == 'upper' or useBBShort2 == 'upper':
            if condBBShort1 and condSuperTrendShort:
                limitOrderPrice = limitOrderPriceShort
                limitOrderDirection = 'Short'
                stopLossPriceShort = calcStopLossPriceShort
                newEntryShort(orderComment=utils.commentOrderCustomseries('enter_short', 'bbUpper'))
        if useBBShort == 'upper2' or useBBShort2 == 'upper2':
            if condBBShort2 and condSuperTrendShort:
                limitOrderPrice = limitOrderPriceShort
                limitOrderDirection = 'Short'
                stopLossPriceShort = calcStopLossPriceShort
                newEntryShort(orderComment=utils.commentOrderCustomseries('enter_short', 'bbUpper2'))
        if useBBShort == 'upper3' or useBBShort2 == 'upper3':
            if condBBShort3 and condSuperTrendShort:
                limitOrderPrice = limitOrderPriceShort
                limitOrderDirection = 'Short'
                stopLossPriceShort = calcStopLossPriceShort
                newEntryShort(orderComment=utils.commentOrderCustomseries('enter_short', 'bbUpper3'))
        if useBBShort == 'lower' or useBBShort2 == 'lower':
            if condBBShort4 and condSuperTrendShort:
                limitOrderPrice = limitOrderPriceShort
                limitOrderDirection = 'Short'
                stopLossPriceShort = calcStopLossPriceShort
                newEntryShort(orderComment=utils.commentOrderCustomseries('enter_short', 'bbLower'))
        if useBBShort == 'lower2' or useBBShort2 == 'lower2':
            if condBBShort5 and condSuperTrendShort:
                limitOrderPrice = limitOrderPriceShort
                limitOrderDirection = 'Short'
                stopLossPriceShort = calcStopLossPriceShort
                newEntryShort(orderComment=utils.commentOrderCustomseries('enter_short', 'bbLower2'))
        if useBBShort == 'lower3' or useBBShort2 == 'lower3':
            if condBBShort6 and condSuperTrendShort:
                limitOrderPrice = limitOrderPriceShort
                limitOrderDirection = 'Short'
                stopLossPriceShort = calcStopLossPriceShort
                newEntryShort(orderComment=utils.commentOrderCustomseries('enter_short', 'bbLower3'))
        if useBBShort3 == 'basis':
            if condBasisShort and condSuperTrendShort:
                limitOrderPrice = limitOrderPriceShort
                limitOrderDirection = 'Short'
                stopLossPriceShort = calcStopLossPriceShort
                newEntryShort(orderComment=utils.commentOrderCustomseries('enter_short', 'maBasis'))
        if useBBShort3 == 'signal':
            if condSignalShort and condSuperTrendShort:
                limitOrderPrice = limitOrderPriceShort
                limitOrderDirection = 'Short'
                stopLossPriceShort = calcStopLossPriceShort
                newEntryShort(orderComment=utils.commentOrderCustomseries('enter_short', 'maSignal'))
        if useMaStrategy and condSuperTrendShort and condMaShort:
            limitOrderPrice = limitOrderPriceShort
            limitOrderDirection = 'Short'
            stopLossPriceShort = calcStopLossPriceShort
            newEntryShort(orderComment=utils.commentOrderCustomseries('enter_short', 'maCross'))
    else:
        if useBBLong == 'lower' or useBBLong2 == 'lower':
            if condBBLong1:
                limitOrderPrice = limitOrderPriceLong
                limitOrderDirection = 'Long'
                stopLossPriceLong = calcStopLossPriceLong
                newEntryLong(orderComment=utils.commentOrderCustomseries('enter_long', 'bbLower'))
        if useBBLong == 'lower2' or useBBLong2 == 'lower2':
            if condBBLong2:
                limitOrderPrice = limitOrderPriceLong
                limitOrderDirection = 'Long'
                stopLossPriceLong = calcStopLossPriceLong
                newEntryLong(orderComment=utils.commentOrderCustomseries('enter_long', 'bbLower2'))
        if useBBLong == 'lower3' or useBBLong2 == 'lower3':
            if condBBLong3:
                limitOrderPrice = limitOrderPriceLong
                limitOrderDirection = 'Long'
                stopLossPriceLong = calcStopLossPriceLong
                newEntryLong(orderComment=utils.commentOrderCustomseries('enter_long', 'bbLower3'))
        if useBBLong == 'upper' or useBBLong2 == 'upper':
            if condBBLong4:
                limitOrderPrice = limitOrderPriceLong
                limitOrderDirection = 'Long'
                stopLossPriceLong = calcStopLossPriceLong
                newEntryLong(orderComment=utils.commentOrderCustomseries('enter_long', 'bbUpper'))
        if useBBLong == 'upper2' or useBBLong2 == 'upper2':
            if condBBLong5:
                limitOrderPrice = limitOrderPriceLong
                limitOrderDirection = 'Long'
                stopLossPriceLong = calcStopLossPriceLong
                newEntryLong(orderComment=utils.commentOrderCustomseries('enter_long', 'bbUpper2'))
        if useBBLong == 'upper3' or useBBLong2 == 'upper3':
            if condBBLong6:
                limitOrderPrice = limitOrderPriceLong
                limitOrderDirection = 'Long'
                stopLossPriceLong = calcStopLossPriceLong
                newEntryLong(orderComment=utils.commentOrderCustomseries('enter_long', 'bbUpper3'))
        if useBBLong3 == 'basis':
            if condBasisLong:
                limitOrderPrice = limitOrderPriceLong
                limitOrderDirection = 'Long'
                stopLossPriceLong = calcStopLossPriceLong
                newEntryLong(orderComment=utils.commentOrderCustomseries('enter_long', 'maBasis'))
        if useBBLong3 == 'signal':
            if condSignalLong:
                limitOrderPrice = limitOrderPriceLong
                limitOrderDirection = 'Long'
                stopLossPriceLong = calcStopLossPriceLong
                newEntryLong(orderComment=utils.commentOrderCustomseries('enter_long', 'maSignal'))
        if useMaStrategy and condMaLong:
            limitOrderPrice = limitOrderPriceLong
            limitOrderDirection = 'Long'
            stopLossPriceLong = calcStopLossPriceLong
            newEntryLong(orderComment=utils.commentOrderCustomseries('enter_long', 'maCross'))
        if useBBShort == 'upper' or useBBShort2 == 'upper':
            if condBBShort1:
                limitOrderPrice = limitOrderPriceShort
                limitOrderDirection = 'Short'
                stopLossPriceShort = calcStopLossPriceShort
                newEntryShort(orderComment=utils.commentOrderCustomseries('Short', 'bbUpper'))
        if useBBShort == 'upper2' or useBBShort2 == 'upper2':
            if condBBShort2:
                limitOrderPrice = limitOrderPriceShort
                limitOrderDirection = 'Short'
                stopLossPriceShort = calcStopLossPriceShort
                newEntryShort(orderComment=utils.commentOrderCustomseries('Short', 'bbUpper2'))
        if useBBShort == 'upper3' or useBBShort2 == 'upper3':
            if condBBShort3:
                limitOrderPrice = limitOrderPriceShort
                limitOrderDirection = 'Short'
                stopLossPriceShort = calcStopLossPriceShort
                newEntryShort(orderComment=utils.commentOrderCustomseries('Short', 'bbUpper3'))
        if useBBShort == 'lower' or useBBShort2 == 'lower':
            if condBBShort4:
                limitOrderPrice = limitOrderPriceShort
                limitOrderDirection = 'Short'
                stopLossPriceShort = calcStopLossPriceShort
                newEntryShort(orderComment=utils.commentOrderCustomseries('Short', 'bbLower'))
        if useBBShort == 'lower2' or useBBShort2 == 'lower2':
            if condBBShort5:
                limitOrderPrice = limitOrderPriceShort
                limitOrderDirection = 'Short'
                stopLossPriceShort = calcStopLossPriceShort
                newEntryShort(orderComment=utils.commentOrderCustomseries('Short', 'bbLower2'))
        if useBBShort == 'lower3' or useBBShort2 == 'lower3':
            if condBBShort6:
                limitOrderPrice = limitOrderPriceShort
                limitOrderDirection = 'Short'
                stopLossPriceShort = calcStopLossPriceShort
                newEntryShort(orderComment=utils.commentOrderCustomseries('Short', 'bbLower3'))
        if useBBShort3 == 'basis':
            if condBasisShort:
                limitOrderPrice = limitOrderPriceShort
                limitOrderDirection = 'Short'
                stopLossPriceShort = calcStopLossPriceShort
                newEntryShort(orderComment=utils.commentOrderCustomseries('Short', 'maBasis'))
        if useBBShort3 == 'signal':
            if condSignalShort:
                limitOrderPrice = limitOrderPriceShort
                limitOrderDirection = 'Short'
                stopLossPriceShort = calcStopLossPriceShort
                newEntryShort(orderComment=utils.commentOrderCustomseries('Short', 'maSignal'))
        if useMaStrategy and condMaShort:
            limitOrderPrice = limitOrderPriceShort
            limitOrderDirection = 'Short'
            stopLossPriceShort = calcStopLossPriceShort
            newEntryShort(orderComment=utils.commentOrderCustomseries('Short', 'maCross'))
    takeTriggerLong: float = high if takeProfitTrigger == 'high/low' else priceMedianHighLow if takeProfitTrigger == 'high/low median' else priceMedianOpenClose if takeProfitTrigger == 'open/close median' else close
    condTakePriceLong: bool = strategy.position_avg_price < close
    condTakeLong1: bool = ta.crossover(takeTriggerLong, bbUpper[1]) and condPositionLong
    condTakeLong2: bool = ta.crossover(takeTriggerLong, bbUpper2[1]) and condPositionLong
    condTakeLong3: bool = ta.crossover(takeTriggerLong, bbUpper3[1]) and condPositionLong
    takeTriggerhort: float = low if takeProfitTrigger == 'high/low' else priceMedianHighLow if takeProfitTrigger == 'high/low median' else priceMedianOpenClose if takeProfitTrigger == 'open/close median' else close
    condTakePriceShort: bool = strategy.position_avg_price > close
    condTakeShort1: bool = ta.crossunder(takeTriggerhort, bbLower[1]) and condPositionShort
    condTakeShort2: bool = ta.crossunder(takeTriggerhort, bbLower2[1]) and condPositionShort
    condTakeShort3: bool = ta.crossunder(takeTriggerhort, bbLower3[1]) and condPositionShort
    if useTakeProfit:
        if condTakeLong1 and condTakePriceLong:
            takeLong(utils.commentOrderCustomseries('take_long', 'bbUpper'))
        if condTakeShort1 and condTakePriceShort:
            takeShort(utils.commentOrderCustomseries('take_short', 'bbLower'))
    if useTakeProfit2:
        if condTakeLong2 and condTakePriceLong:
            takeLong(utils.commentOrderCustomseries('take_long', 'bbUpper2'))
        if condTakeShort2 and condTakePriceShort:
            takeShort(utils.commentOrderCustomseries('take_short', 'bbLower2'))
    if useTakeProfit3:
        if condTakeLong3 and condTakePriceLong:
            stopLossPriceLong = calcStopLossPriceLong
            takeLong(utils.commentOrderCustomseries('take_long', 'bbUpper3'))
        if condTakeShort3 and condTakePriceShort:
            stopLossPriceShort = calcStopLossPriceShort
            takeShort(utils.commentOrderCustomseries('take_short', 'bbLower3'))
    condStopSuperTrendLong: bool = barCrossoverCounter(supertrendDirection, 0) == 1 and condPositionLong
    condStopSuperTrendShort: bool = barCrossunderCounter(supertrendDirection, 0) == 1 and condPositionShort
    condStopFlexSuperTrendLong: bool = counterEvent(condPositionLong, condSuperTrendShort) == 1
    condStopFlexMaLong: bool = counterEvent(condPositionLong, condMaShort) == 1
    condStopFlexSuperTrendShort: bool = counterEvent(condPositionShort, condSuperTrendLong) == 1
    condStopFlexMaShort: bool = counterEvent(condPositionShort, condMaLong) == 1
    if stopLossType == 'SuperTrend + ATR':
        if condStopSuperTrendLong:
            stopLossPriceLong = supertrend[1] - stopLossAtr * SLAtrMultiplierLong
    if stopLossType == 'SuperTrend + ATR':
        if condStopSuperTrendShort:
            stopLossPriceShort = supertrend[1] + stopLossAtr * SLAtrMultiplierShort
    if useFlexStopLoss:
        if stopLossType == 'ATR' or stopLossType == 'StdDev':
            if condStopFlexSuperTrendLong:
                stopLossPriceLong = stopLossPriceLong + stopLossAtr * SLAtrMultiplierLong * SLFlexMult
            if condStopFlexMaLong:
                stopLossPriceLong = stopLossPriceLong + stopLossAtr * SLAtrMultiplierLong * SLFlexMult
            if condStopFlexSuperTrendShort:
                stopLossPriceShort = stopLossPriceShort - stopLossAtr * SLAtrMultiplierLong * SLFlexMult
            if condStopFlexMaShort:
                stopLossPriceShort = stopLossPriceShort - stopLossAtr * SLAtrMultiplierLong * SLFlexMult
    stopTriggerLong: float = low if stopLossTrigger == 'high/low' else priceMedianHighLow if stopLossTrigger == 'high/low median' else priceMedianOpenClose if stopLossTrigger == 'open/close median' else close
    condStopLong: bool = stopTriggerLong < stopLossPriceLong and condPositionLong
    stopTriggerShort: float = high if stopLossTrigger == 'high/low' else priceMedianHighLow if stopLossTrigger == 'high/low median' else priceMedianOpenClose if stopLossTrigger == 'open/close median' else close
    condStopShort: bool = stopTriggerShort > stopLossPriceShort and condPositionShort
    if stopLossType != 'off':
        if useSuperTrend:
            if condStopLong and condSuperTrendShort:
                stopLossLong(utils.commentOrderCustomseries('stop_long', 'stop'))
                if limitOrderDirection == 'Long':
                    limitOrderPrice = na
                    limitOrderDirection = 'flat'
            if condStopShort and condSuperTrendLong:
                if limitOrderDirection == 'Short':
                    limitOrderPrice = na
                    limitOrderDirection = 'flat'
                stopLossShort(utils.commentOrderCustomseries('stop_short', 'stop'))
        else:
            if condStopLong:
                if limitOrderDirection == 'Long':
                    limitOrderPrice = na
                    limitOrderDirection = 'flat'
                stopLossLong(utils.commentOrderCustomseries('stop_long', 'stop'))
            if condStopShort:
                if limitOrderDirection == 'Short':
                    limitOrderPrice = na
                    limitOrderDirection = 'flat'
                stopLossShort(utils.commentOrderCustomseries('stop_short', 'stop'))
    condLimitPrirceExist: bool = na(limitOrderPrice) == False
    if useLimitOrder and condLimitPrirceExist:
        __loop_1__ = pine_loop(1, 1)
        while __loop_1__.step(strategy.opentrades):
            i = __loop_1__.value
            if math.abs(limitOrderPrice - strategy.opentrades.entry_price(strategy.opentrades - i)) < epsilon:
                limitOrderPrice = na
                limitOrderDirection = 'flat'
    colorGreen: Color = color.new('#00FF08CC')
    colorGreen2: Color = color.new('#00FF0863')
    colorGreen3: Color = color.new('#089981')
    colorRed: Color = color.new('#FF0000D4')
    colorRed2: Color = color.new('#FF000071')
    colorPurple: Color = color.new('#8400FF23')
    colorPurple2: Color = color.new('#45008657')
    colorPurple3: Color = color.new('#8400FF09')
    colorOrange: Color = color.new('#F57B00C7')
    colorBlack = color.rgb(70, 70, 70, 50)
    pPriceMedian = plot(priceMedianOpenClose if useSuperTrend else na, '[Price Median]', color=color.black, linewidth=1, style=plot.style_line, display=display.none)
    pSuperTrend = plot(supertrend if useSuperTrend else na, '[SuperTrend]', color=colorGreen2 if condSuperTrendLong else colorRed2, linewidth=2, style=plot.style_line, display=display.pane if useSuperTrend else display.none)
    fill(pPriceMedian, pSuperTrend, title='[SuperTrend] Background', color=color.rgb(0, 255, 8, 90) if condSuperTrendLong else color.rgb(255, 0, 0, 90), display=display.all)
    basis = plot(maBasis, '[MA] Basis', color=colorGreen2 if maSignal > maBasis else colorRed2, linewidth=1, style=plot.style_line, display=display.pane)
    signal = plot(maSignal, '[MA] Signal', color=colorGreen2 if maSignal > maBasis else colorRed2, linewidth=1, style=plot.style_line, display=display.pane)
    plot(maBasis if ta.crossover(maSignal, maBasis) else na, '[MA] Long signal', color=colorGreen, style=plot.style_circles, linewidth=4, display=display.pane)
    plot(maBasis if ta.crossunder(maSignal, maBasis) else na, '[MA] Short signal', color=colorRed, style=plot.style_circles, linewidth=4, display=display.pane)
    fill(basis, signal, title='[MA] Background', color=colorGreen2 if maSignal > maBasis else colorRed2, display=display.all)
    plotCondStopLossLong: bool = condPositionLong and condSuperTrendShort if useSuperTrend else condPositionLong
    plotCondStopLossShort: bool = condPositionShort and condSuperTrendLong if useSuperTrend else condPositionShort
    plot(stopLossPriceLong if condPositionLong else na, 'Stop-loss price: Long', color=colorRed if plotCondStopLossLong else colorOrange, style=plot.style_linebr, linewidth=2, display=display.none)
    plot(stopLossPriceShort if condPositionShort else na, 'Stop-loss price: Short', color=colorRed if plotCondStopLossShort else colorOrange, style=plot.style_linebr, linewidth=2, display=display.none)
    u1 = plot(bbUpper, '[BB] Upper', color=colorPurple, display=display.pane)
    l1 = plot(bbLower, '[BB] Lower', color=colorPurple, display=display.pane)
    u2 = plot(bbUpper2, '[BB] Upper 2', color=colorPurple, display=display.pane)
    l2 = plot(bbLower2, '[BB] Lower 2', color=colorPurple, display=display.pane)
    u3 = plot(bbUpper3, '[BB] Upper 2', color=colorPurple, display=display.pane)
    l3 = plot(bbLower3, '[BB] Lower 2', color=colorPurple, display=display.pane)
    fill(u1, l1, title='[BB] Background 1-1', color=colorPurple3, display=display.all)
    fill(u2, l2, title='[BB] Background 2-2', color=colorPurple3, display=display.all)
    fill(u3, l3, title='[BB] Background 3-3', color=colorPurple3, display=display.all)
    currentPosition: Persistent[str] = 'flat'
    currentPosition = 'Long ↗' if strategy.position_size > 0 else 'Short ↘'
    if strategy.position_size == 0:
        currentPosition = 'flat'
    condPositionExist: bool = currentPosition == 'Long ↗' or currentPosition == 'Short ↘'
    lastEntryPrice: float = strategy.opentrades.entry_price(strategy.opentrades - 1)
    positionTable: Persistent[Table] = table.new(position=position.top_right, columns=2, rows=5)
    table.cell(table_id=positionTable, column=1, row=0, text='Position', bgcolor=colorBlack, text_color=color.white, text_halign=text.align_right, tooltip=strategy.opentrades.entry_comment(strategy.opentrades - 1) if strategy.opentrades == 1 else na)
    table.clear(positionTable, 0, 1, 1, 4)
    table.cell(table_id=positionTable, column=0, row=1, text='Direction:', bgcolor=colorBlack, text_color=color.white, text_halign=text.align_left)
    table.cell(table_id=positionTable, column=1, row=1, text=currentPosition, bgcolor=colorBlack if strategy.opentrades == 0 else colorRed2 if condPositionShort else colorGreen3, text_color=color.rgb(255, 255, 255), text_halign=text.align_right)
    if condPositionExist:
        table.cell(table_id=positionTable, column=0, row=2, text='Amount:', bgcolor=colorBlack, text_color=color.white, text_halign=text.align_left)
        table.cell(table_id=positionTable, column=1, row=2, text=string.tostring(strategy.position_size), bgcolor=colorBlack, text_color=color.white, text_halign=text.align_right)
        if strategy.opentrades > 1:
            table.cell(table_id=positionTable, column=0, row=3, text='Avg. price:', bgcolor=colorBlack, text_color=color.white, text_halign=text.align_left)
            table.cell(table_id=positionTable, column=1, row=3, text=string.tostring(strategy.position_avg_price, '#.###'), bgcolor=colorBlack, text_color=color.white, text_halign=text.align_right)
        if strategy.opentrades == 1:
            table.cell(table_id=positionTable, column=0, row=3, text='Entry price:', bgcolor=colorBlack, text_color=color.white, text_halign=text.align_left, tooltip=strategy.opentrades.entry_comment(strategy.opentrades - 1) if strategy.opentrades == 1 else na)
            table.cell(table_id=positionTable, column=1, row=3, text=string.tostring(strategy.opentrades.entry_price(strategy.opentrades - 1), '#.###'), bgcolor=colorBlack, text_color=color.white, text_halign=text.align_right)
        if stopLossType != 'off':
            table.cell(table_id=positionTable, column=0, row=4, text='Stop Loss:', bgcolor=colorBlack, text_color=color.white)
            table.cell(table_id=positionTable, column=1, row=4, text=string.tostring(stopLossPriceLong if strategy.position_size > 0 else stopLossPriceShort, '#.###'), bgcolor=colorBlack, text_color=color.white)
    entriesTable: Persistent[Table] = table.new(position=position.middle_right, columns=2, rows=6)
    if strategy.opentrades > 1 and strategy.opentrades < 5:
        table.cell(table_id=entriesTable, column=1, row=0, text='Entries', bgcolor=colorBlack, text_color=color.white, text_halign=text.align_right)
        table.clear(entriesTable, 0, 1, 1, 5)
        __loop_1__ = pine_loop(1, 1)
        while __loop_1__.step(strategy.opentrades):
            i = __loop_1__.value
            table.cell(table_id=entriesTable, column=0, row=0 + i, text='#' + string.tostring(i), bgcolor=colorBlack, text_color=color.white, text_halign=text.align_left)
            table.cell(table_id=entriesTable, column=1, row=0 + i, text=string.tostring(strategy.opentrades.entry_price(strategy.opentrades - i)) + ' 💬', bgcolor=colorBlack, text_color=color.white, text_halign=text.align_right, tooltip=strategy.opentrades.entry_comment(strategy.opentrades - i))
    elif strategy.opentrades <= 1:
        table.clear(entriesTable, 0, 0, 1, 5)
    if useLimitOrder:
        limitOrderTable: Persistent[Table] = table.new(position=position.bottom_right, columns=2, rows=3)
        table.clear(limitOrderTable, 0, 0, 1, 2)
        if na(limitOrderPrice) == False:
            table.cell(table_id=limitOrderTable, column=1, row=0, text='Limit order', bgcolor=colorBlack, text_color=color.white, text_halign=text.align_right)
            table.cell(table_id=limitOrderTable, column=0, row=1, text='Direction:', bgcolor=colorBlack, text_color=color.white, text_halign=text.align_left)
            table.cell(table_id=limitOrderTable, column=1, row=1, text=string.tostring(limitOrderDirection), bgcolor=colorRed2 if limitOrderDirection == 'Short' else colorGreen3, text_color=color.white, text_halign=text.align_right)
            table.cell(table_id=limitOrderTable, column=0, row=2, text='Price:', bgcolor=colorBlack, text_color=color.white, text_halign=text.align_left)
            table.cell(table_id=limitOrderTable, column=1, row=2, text=string.tostring(limitOrderPrice), bgcolor=colorBlack, text_color=color.white, text_halign=text.align_right)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)