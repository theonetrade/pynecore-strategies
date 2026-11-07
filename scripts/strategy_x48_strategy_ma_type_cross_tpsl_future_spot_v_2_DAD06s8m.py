"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    barcolor, barmerge, close, color, currency, fill, fixnan, high, input,
    location, low, na, ohlc4, plot, plotshape, request, script, shape, size, strategy, string,
    syminfo, ta, time, timeframe, timestamp
)
from pynecore.types import Persistent, Series
import lib.X4815162342.X48_LibaryStrategyStatus.v2 as fuLi

Text_Alert_Future: str = '{{strategy.order.alert_message}}'
BTR1: str = '════════ INPUT BACKTEST TIME RANGE ════════'


@script.strategy('X48 - Strategy | MA Multi Type Cross + TPSL + Swing + Surfing&Diving| Future&Spot | V.3.6', overlay=True, default_qty_type=strategy.cash, default_qty_value=20, initial_capital=200, currency=currency.USD, commission_value=0.1, slippage=0, margin_long=0, margin_short=0, close_by_id=True)
def main(
    SMODE=input.bool(title='SPOT MODE', defval=False, group='= SPOT SETTING =', tooltip='SPOT = Disable Short Position'),
    srcstrategy: Series[float] = input(close, title='Source Multi MA', group='= Multi MA SETTING =', tooltip='Normal Line = Close \nSmooth Line = ohlc4'),
    fastSW=input.bool(title='Show Fast MA Line', defval=True, group='= Multi MA SETTING ='),
    slowSW=input.bool(title='Show Slow MA Line', defval=True, group='= Multi MA SETTING ='),
    ma1strategy=input(18, title='Fast MA Length', group='= Multi MA SETTING ='),
    type1strategy=input.string('EMA', 'Fast MA Type', options=('SMA', 'EMA', 'WMA', 'HMA', 'RMA', 'VWMA'), group='= Multi MA SETTING =', tooltip='SMA / EMA / WMA / HMA / RMA / VWMA'),
    MA2_MODE=input.bool(title='MA MIDDLE MODE', defval=False, group='= MIDDLE 3MA SETTING =', tooltip='Strategy Is\nMA Fast > MA Slow = Long\nEMA Fast < MA Mid = Short'),
    ma2strategy=input(24, title='Middle MA Length', group='= MIDDLE 3MA SETTING ='),
    type2strategy=input.string('EMA', 'Middle MA Type', options=('SMA', 'EMA', 'WMA', 'HMA', 'RMA', 'VWMA'), group='= MIDDLE 3MA SETTING =', tooltip='SMA / EMA / WMA / HMA / RMA / VWMA'),
    ma3strategy=input(34, title='Slow MA Length', group='= Multi MA SETTING ='),
    type3strategy=input.string('EMA', 'Slow MA Type', options=('SMA', 'EMA', 'WMA', 'HMA', 'RMA', 'VWMA'), group='= Multi MA SETTING =', tooltip='SMA / EMA / WMA / HMA / RMA / VWMA'),
    copy_Fu=input(defval=Text_Alert_Future, title='Alert Message for BOT', inline='00', group='═ Bot Setting ═ \n >> If You Dont Use Bot Just Pass It', tooltip='Alert For X48-BOT > Copy and Paste To Alert Function'),
    passphrase=input.string(defval='1234', title='Bot Pass', group='═ Bot Setting ═ \n >> If You Dont Use Bot Just Pass It', tooltip='Passphrase Must Be Same as X48-BOT'),
    leveragex=input.int(125, title='leverage', group='═ Bot Setting ═ \n >> If You Dont Use Bot Just Pass It', tooltip='"NOTHING" to do with Position size For Command To X48-BOT Only', minval=1),
    longcommand=input.string(defval='AutoLong', title='Bot Long Command', group='═ Bot Setting ═ \n >> If You Dont Use Bot Just Pass It', tooltip='1.OpenLong\n2.AutoLong\n***If AutoLong = Close(100%) First > Open Long Position Auto'),
    shortcommand=input.string(defval='AutoShort', title='Bot Short Command', group='═ Bot Setting ═ \n >> If You Dont Use Bot Just Pass It', tooltip='1.OpenShort\n2.AutoShort\n***If AutoShort = Close(100%) First > Open Short Position Auto'),
    markettype=input.string(defval='bnfuture', title='Future/Spot Command', group='═ Bot Setting ═ \n >> If You Dont Use Bot Just Pass It', tooltip='1. bnfuture = FUTURE MODE\n2. bnspot = SPOT MODE\n 3.bncombo = EZ 2in1 Order'),
    RSI_MODE=input.bool(title='RSI MODE', defval=False, group='= RSI SETTING >> COMFIRM RSI BEFORE OPEN POSITION =', tooltip='If Mode On = Use RSI Strategy With Long and Short\n >> RSI Confirm Before Open Position'),
    RSILength=input(14, title='RSI Length', group='= RSI SETTING >> PLOT RSI SIGNAL OB OS ='),
    OverBought=input(70, title='RSI OB', group='= RSI SETTING >> PLOT RSI SIGNAL OB OS =', tooltip='Lil Cross Symbol'),
    OverSold=input(30, title='RSI OS', group='= RSI SETTING >> PLOT RSI SIGNAL OB OS =', tooltip='Lil Diamond Symbol'),
    MACD_MODE_SIG=input.bool(title='MACD MODE = MACD Cross Signal', defval=False, group='= MACD SETTING =', tooltip='If Mode On = Use MACD Strategy for Signal When Cross Up and Cross Down'),
    MACDfastLength=input(12, title='MACD Fast', group='= MACD SETTING ='),
    MACDslowlength=input(26, title='MACD Slow', group='= MACD SETTING ='),
    MACDLength=input(18, title='MACD Length', group='= MACD SETTING ='),
    SURF_DIVE_MODE=input.bool(title='SURFING&DIVING MODE', defval=False, group='= SURF&DIVING SETTING =', tooltip='How To Use\n3 Dot Waves CrossUp Purple Line = Bullish Trend\n3 Dot Waves CrossDown Purple Line = Bearish Trend\n\nBig Blue Dot is Surfing Zone\nCandle Price Close > Surfing Zone = Lil Bullish\nCandle Price Clsoe < Surfing Zone = Lil Bearish'),
    showSurf=input(False, title='Show Surfing & Diving Signal', group='= SURF&DIVING SETTING =', tooltip='Plot Symbol of Lil Trend By Surfing Man'),
    mode=input.bool(title='Mode AUTO TP/SL', defval=True, group='= AUTO TP/SL =', tooltip='If Mode On = Use TP/SL\nIf Mode Off = Turn Off TP/SL Effect\nTP = 1000%+ for nonlimit TP Length \nSL = 1-100% if 100% Its Mean Liq. Position'),
    __input_28__=input.float(0, title='TP [LONG] %', group='= AUTO TP/SL =', tooltip='Disable = 0 (non limit profit)'),
    __input_29__=input.float(0, title='TP [SHORT] %', group='= AUTO TP/SL =', tooltip='Disable = 0 (non limit profit)'),
    __input_30__=input.float(0, title='Auto Stop Loss %', group='= AUTO TP/SL =', tooltip='Disable = 0 (non limit Stop Loss)'),
    BOTrail_MODE=input.bool(defval=False, title='🅾️ CALLBACK Trailing Stop Mode', group='= AUTO TP/SL =', tooltip='BreakOut Length For Who\'s Want Fast Trailing But This Low Profit But More Time For TP\nIt\'s Can Combo With Breakout and 15m'),
    lengthBO=input.int(title='1️⃣ Length CallBack', minval=1, maxval=1000, defval=5, group='= AUTO TP/SL ='),
    triling_BO=input.float(title='🅾️ BreakOut Trailing CALLBACK [%]', defval=25, minval=0.01, maxval=999.99, group='= AUTO TP/SL =', tooltip='Binance Callback = 5%, Now You Can Customize Your Callback ><'),
    i_startTime=input.time(defval=timestamp('01 Jan 1945 00:00 +0000'), title='Start', inline='timestart', group=BTR1, tooltip='Start Backtest YYYY/MM/DD'),
    i_endTime=input.time(defval=timestamp('01 Jan 2074 23:59 +0000'), title='End', inline='timeend', group=BTR1, tooltip='End Backtest YYYY/MM/DD'),
    srccdc: Series[float] = input(title='Data Array', defval=ohlc4, group='Bar Paint Color Red/Blue/Yellow/Green', tooltip='Just Bar Paint Only\nNo Effect For EMA/SMA Line'),
    Swing_MODE=input.bool(title='SWING MODE', defval=True, group='= SWING SETTING =', tooltip='If Mode On = Plot Swing High and Swing Low'),
    pvtLenL=input.int(6, minval=1, title='Pivot Length Left Hand Side', group='= SWING SETTING ='),
    pvtLenR=input.int(6, minval=1, title='Pivot Length Right Hand Side', group='= SWING SETTING ='),
    showStop=input(True, title='Show Recent Low Stop?', group='= SWING SETTING ='),
    TRAILING_MODE=input.bool(title='TRAILING MODE', defval=False, group='= TRAILING TP/SL SETTING =', tooltip='When Candle Price Close > or < Trailing Line\nShould TP or SL by Your Position'),
    BG_MODE=input.bool(title='BACKGROUND PAINT MODE', defval=True, group='= BACKGROUND PAINT SETTING =', tooltip='Just Fill Background Color and Paint Line Between Space'),
    show_Net=input.bool(True, 'Monitor Profit&Loss', inline='Lnet', group='= PNL MONITOR SETTING ='),
    position_=input.string('bottom_center', 'Position', options=('top_right', 'middle_right', 'bottom_right', 'top_center', 'middle_center', 'bottom_center', 'middle_left', 'bottom_left'), inline='Lnet'),
    size_i=input.string('auto', 'size', options=('auto', 'tiny', 'small', 'normal'), inline='Lnet'),
    color_Net=input.color(color.blue, '', inline='Lnet')
):
    pricestrategy = request.security(syminfo.tickerid, timeframe.period, srcstrategy)
    __block_result__ = na
    __switch__ = type1strategy
    if __switch__ == 'EMA':
        __block_result__ = ta.ema(pricestrategy, ma1strategy)
    elif __switch__ == 'SMA':
        __block_result__ = ta.sma(pricestrategy, ma1strategy)
    elif __switch__ == 'WMA':
        __block_result__ = ta.wma(pricestrategy, ma1strategy)
    elif __switch__ == 'HMA':
        __block_result__ = ta.hma(pricestrategy, ma1strategy)
    elif __switch__ == 'RMA':
        __block_result__ = ta.rma(pricestrategy, ma1strategy)
    elif __switch__ == 'VWMA':
        __block_result__ = ta.vwma(pricestrategy, ma1strategy)
    price1strategy = __block_result__
    __block_result_1__ = na
    __switch__ = type2strategy
    if __switch__ == 'EMA':
        __block_result_1__ = ta.ema(pricestrategy, ma2strategy)
    elif __switch__ == 'SMA':
        __block_result_1__ = ta.sma(pricestrategy, ma2strategy)
    elif __switch__ == 'WMA':
        __block_result_1__ = ta.wma(pricestrategy, ma2strategy)
    elif __switch__ == 'HMA':
        __block_result_1__ = ta.hma(pricestrategy, ma2strategy)
    elif __switch__ == 'RMA':
        __block_result_1__ = ta.rma(pricestrategy, ma2strategy)
    elif __switch__ == 'VWMA':
        __block_result_1__ = ta.vwma(pricestrategy, ma2strategy)
    price2strategy = __block_result_1__
    __block_result_2__ = na
    __switch__ = type3strategy
    if __switch__ == 'EMA':
        __block_result_2__ = ta.ema(pricestrategy, ma3strategy)
    elif __switch__ == 'SMA':
        __block_result_2__ = ta.sma(pricestrategy, ma3strategy)
    elif __switch__ == 'WMA':
        __block_result_2__ = ta.wma(pricestrategy, ma3strategy)
    elif __switch__ == 'HMA':
        __block_result_2__ = ta.hma(pricestrategy, ma3strategy)
    elif __switch__ == 'RMA':
        __block_result_2__ = ta.rma(pricestrategy, ma3strategy)
    elif __switch__ == 'VWMA':
        __block_result_2__ = ta.vwma(pricestrategy, ma3strategy)
    price3strategy = __block_result_2__
    Alert_OpenLong: str = '{"ex":"' + markettype + '","side": "' + longcommand + '", "amount": "@{{strategy.order.contracts}}", "symbol": "{{ticker}}", "passphrase": "' + passphrase + '","leverage":"' + string.tostring(leveragex) + '"}'
    Alert_OpenShort: str = '{"ex":"' + markettype + '","side": "' + shortcommand + '", "amount": "@{{strategy.order.contracts}}", "symbol": "{{ticker}}", "passphrase": "' + passphrase + '","leverage":"' + string.tostring(leveragex) + '"}'
    Alert_StopLosslong: str = '{"ex":"' + markettype + '","side": "CloseLong", "amount": "%100", "symbol": "{{ticker}}", "passphrase": "' + passphrase + '","leverage":"' + string.tostring(leveragex) + '"}'
    Alert_StopLossshort: str = '{"ex":"' + markettype + '","side": "CloseShort", "amount": "%100", "symbol": "{{ticker}}", "passphrase": "' + passphrase + '","leverage":"' + string.tostring(leveragex) + '"}'
    vrsi = ta.rsi(srcstrategy, RSILength)
    RSIUP = ta.crossover(vrsi, OverBought)
    RSIDOWN = ta.crossunder(vrsi, OverSold)
    plotshape(RSIUP if RSI_MODE else False, title='RSIUP', text='⏰', color=color.new(color.yellow, 100), style=shape.circle, location=location.belowbar, size=size.tiny)
    plotshape(RSIDOWN if RSI_MODE else False, title='RSIDOWN', text='☀️', color=color.new(color.red, 100), style=shape.circle, location=location.abovebar, size=size.tiny)
    MACD = ta.ema(close, MACDfastLength) - ta.ema(close, MACDslowlength)
    aMACD = ta.ema(MACD, MACDLength)
    delta = MACD - aMACD
    macdTPl = ta.crossover(delta, 0)
    macdTPs = ta.crossunder(delta, 0)
    plotshape(macdTPl if MACD_MODE_SIG else False, title='macdTPl', text='💎', color=color.new(color.yellow, 100), style=shape.circle, location=location.belowbar, size=size.tiny)
    plotshape(macdTPs if MACD_MODE_SIG else False, title='macdTPs', text='💎', color=color.new(color.red, 100), style=shape.circle, location=location.abovebar, size=size.tiny)
    surfing_21 = ta.ema(close, 21)
    diving_144 = ta.ema(close, 144)
    diving_233 = ta.ema(close, 233)
    surfing_h = ta.sma(high, 34)
    surfing_c = ta.sma(close, 34)
    surfing_l = ta.sma(low, 34)
    surfingup = ta.crossover(close, surfing_21)
    surfingdown = ta.crossunder(close, surfing_21)
    plotshowSurf = showSurf if SURF_DIVE_MODE == True else False
    plotshape(surfingup if showSurf else False, 'SurfingUp', location=location.belowbar, text='🏄\u200d♂️')
    plotshape(surfingdown if showSurf else False, 'SurfingDown', location=location.abovebar, text='🏄')
    plot(surfing_21 if SURF_DIVE_MODE else na, 'surfing_21', color=color.new(color.new('#6EB0FF'), 20), linewidth=1, style=plot.style_stepline_diamond)
    plot(surfing_h if SURF_DIVE_MODE else na, 'surfing_h', color=color.aqua, linewidth=1, style=plot.style_circles)
    plot(surfing_c if SURF_DIVE_MODE else na, 'surfing_c', color=color.silver, linewidth=1, style=plot.style_circles)
    plot(surfing_l if SURF_DIVE_MODE else na, 'surfing_l', color=color.blue, linewidth=1, style=plot.style_circles)
    plot(diving_144 if SURF_DIVE_MODE else na, 'diving_144', color=color.purple, linewidth=2, style=plot.style_line)
    plot(diving_233 if SURF_DIVE_MODE else na, 'diving_233', color=color.new('#FF00FF'), linewidth=2, style=plot.style_line)
    def tpsl(percent):
        return strategy.position_avg_price * percent / 100 / syminfo.mintick

    tp_l = tpsl(__input_28__)
    tp_s = tpsl(__input_29__)
    sl = tpsl(__input_30__)
    upBound = ta.highest(high, lengthBO)
    downBound = ta.lowest(low, lengthBO)
    SL_LongBO = close < upBound - upBound * triling_BO / 100
    SL_ShortBO = close > downBound + downBound * triling_BO / 100
    def calcStopLossPrice(OffsetPts):
        __block_result_3__ = na
        if strategy.position_size > 0:
            __block_result_3__ = strategy.position_avg_price - OffsetPts * syminfo.mintick
        elif strategy.position_size < 0:
            __block_result_3__ = strategy.position_avg_price + OffsetPts * syminfo.mintick
        else:
            __block_result_3__ = na
        return __block_result_3__

    def calcStopLossL_AlertPrice(OffsetPts):
        return strategy.position_avg_price - OffsetPts * syminfo.mintick

    def calcStopLossS_AlertPrice(OffsetPts):
        return strategy.position_avg_price + OffsetPts * syminfo.mintick

    def calcTakeProfitPrice(OffsetPts):
        __block_result_4__ = na
        if strategy.position_size > 0:
            __block_result_4__ = strategy.position_avg_price + OffsetPts * syminfo.mintick
        elif strategy.position_size < 0:
            __block_result_4__ = strategy.position_avg_price - OffsetPts * syminfo.mintick
        else:
            __block_result_4__ = na
        return __block_result_4__

    def calcTakeProfitL_AlertPrice(OffsetPts):
        return strategy.position_avg_price + OffsetPts * syminfo.mintick

    def calcTakeProfitS_AlertPrice(OffsetPts):
        return strategy.position_avg_price - OffsetPts * syminfo.mintick

    stoploss: Persistent[float] = 0.0
    stoploss_l: Persistent[float] = 0.0
    stoploss_s: Persistent[float] = 0.0
    takeprofit: Persistent[float] = 0.0
    takeprofit_l: Persistent[float] = 0.0
    takeprofit_s: Persistent[float] = 0.0
    takeprofit_ll: Persistent[float] = 0.0
    takeprofit_ss: Persistent[float] = 0.0
    if mode == True:
        if strategy.position_size > 0:
            if sl > 0:
                stoploss = calcStopLossPrice(sl)
                stoploss_l = stoploss
            elif sl <= 0:
                stoploss = na
            if tp_l > 0:
                takeprofit = tp_l
                takeprofit_ll = close + close / 100 * tp_l
            elif tp_l <= 0:
                takeprofit = na
        if strategy.position_size < 0:
            if sl > 0:
                stoploss = calcStopLossPrice(sl)
                stoploss_s = stoploss
            elif sl <= 0:
                stoploss = na
            if tp_s > 0:
                takeprofit = tp_s
                takeprofit_ss = close - close / 100 * tp_s
            elif tp_s <= 0:
                takeprofit = na
        elif strategy.position_size == 0:
            stoploss = na
            takeprofit = na
    if time >= i_startTime and time <= i_endTime:
        if MA2_MODE == False:
            longCondition = ta.crossover(price1strategy, price3strategy)
            if longCondition:
                strategy.entry('Long', strategy.long, alert_message=Alert_OpenLong, comment='🌙')
            shortCondition = ta.crossunder(price1strategy, price3strategy)
            if shortCondition and SMODE == True:
                strategy.close('Long', qty_percent=100, comment='🎃')
            if shortCondition and SMODE == False:
                strategy.entry('Short', strategy.short, alert_message=Alert_OpenShort, comment='👻')
        if MA2_MODE == True:
            longCondition = ta.crossover(price1strategy, price3strategy)
            if longCondition:
                strategy.entry('Long', strategy.long, alert_message=Alert_OpenLong, comment='🌙')
            shortCondition = ta.crossunder(price1strategy, price3strategy)
            StopshortCondition = ta.crossunder(price1strategy, price2strategy)
            if StopshortCondition and SMODE == True:
                strategy.close('Long', qty_percent=100, comment='🎃')
            if StopshortCondition and SMODE == False:
                strategy.close('Long', qty_percent=100, comment='🎃')
            if shortCondition and SMODE == False:
                strategy.entry('Short', strategy.short, alert_message=Alert_OpenShort, comment='👻')
    if mode == True:
        if SMODE == False:
            if strategy.position_size > 0:
                strategy.exit('Exit', 'Long', qty_percent=100, profit=takeprofit, stop=stoploss, comment_profit='TP💚L', comment_loss='SL💚L', alert_message=Alert_StopLosslong)
            if strategy.position_size < 0:
                strategy.exit('Exit', 'Short', qty_percent=100, profit=takeprofit, stop=stoploss, comment_profit='TP❤️️S', comment_loss='SL❤️️S', alert_message=Alert_StopLossshort)
        elif SMODE == True:
            if strategy.position_size > 0:
                strategy.exit('Exit', 'Long', qty_percent=100, profit=takeprofit, stop=stoploss, comment_profit='TP💚L', comment_loss='SL💚L', alert_message=Alert_StopLosslong)
    if BOTrail_MODE == True:
        if SMODE == False:
            if SL_LongBO and strategy.position_size > 0:
                strategy.close('Long', qty_percent=100, comment='❇️CALLBACK❇️', alert_message=Alert_StopLosslong)
            if SL_ShortBO and strategy.position_size < 0:
                strategy.close('Short', qty_percent=100, comment='❇️CALLBACK❇️', alert_message=Alert_StopLossshort)
        elif SMODE == True:
            if SL_LongBO and strategy.position_size > 0:
                strategy.close('Long', qty_percent=100, comment='❇️CALLBACK❇️', alert_message=Alert_StopLosslong)
    APcdc = ta.ema(srccdc, 2)
    Bullish: Series = price1strategy > price3strategy
    Bearish: Series = price1strategy < price3strategy
    Green = Bullish and APcdc > price1strategy
    Red = Bearish and APcdc < price1strategy
    Yellow = Bullish and APcdc < price1strategy
    Blue = Bearish and APcdc > price1strategy
    Buycdc = Bullish and Bearish[1]
    Sellcdc = Bearish and Bullish[1]
    bcolor = color.lime if Green else color.red if Red else color.yellow if Yellow else color.blue if Blue else color.white
    barcolor(color=bcolor)
    FastL = plot(price1strategy if fastSW else na, 'Fast MA', color=color.new(color.red, 0), style=plot.style_line, linewidth=2)
    MidL = plot(price2strategy if MA2_MODE else na, 'Middle MA', color=color.new(color.blue, 0), style=plot.style_line, linewidth=2)
    SlowL = plot(price3strategy if slowSW else na, 'Slow MA', color=color.new(color.yellow, 0), style=plot.style_line, linewidth=2)
    fillcolor = color.new(color.green, 90) if Bullish else color.new(color.red, 90) if Bearish else color.new(color.black, 90)
    pvthi_: Series = ta.pivothigh(high, pvtLenL, pvtLenR)
    pvtlo_: Series = ta.pivotlow(low, pvtLenL, pvtLenR)
    Shunt: int = 1
    maxLvlLen: int = 0
    pvthi = pvthi_[Shunt]
    pvtlo = pvtlo_[Shunt]
    counthi = ta.barssince(not na(pvthi))
    countlo = ta.barssince(not na(pvtlo))
    pvthis = fixnan(pvthi)
    pvtlos = fixnan(pvtlo)
    hipc = na if ta.change(pvthis) != 0 else color.maroon
    lopc = na if ta.change(pvtlos) != 0 else color.green
    plot((pvthis if maxLvlLen == 0 or counthi < maxLvlLen else na) if Swing_MODE else na, color=hipc, linewidth=1, offset=-pvtLenR - Shunt, title='Top Levels')
    plot((pvtlos if maxLvlLen == 0 or countlo < maxLvlLen else na) if Swing_MODE else na, color=lopc, linewidth=1, offset=-pvtLenR - Shunt, title='Bottom Levels')
    plot((pvthis if maxLvlLen == 0 or counthi < maxLvlLen else na) if Swing_MODE else na, color=hipc, linewidth=1, offset=0, title='Top Levels 2')
    plot((pvtlos if maxLvlLen == 0 or countlo < maxLvlLen else na) if Swing_MODE else na, color=lopc, linewidth=1, offset=0, title='Bottom Levels 2')
    stopLevel = ta.valuewhen(cast_bool(pvtlo_), low[pvtLenR], 0)
    plotStopLevel = stopLevel if showStop == True else na
    plot(plotStopLevel if Swing_MODE else na, style=plot.style_linebr, color=color.new(color.orange, 50), show_last=1, linewidth=2, trackprice=True)
    c480 = request.security(syminfo.tickerid, 'M', close, barmerge.gaps_off, barmerge.lookahead_on)
    c4801 = request.security(syminfo.tickerid, 'M', close[1], barmerge.gaps_off, barmerge.lookahead_on)
    c4802 = request.security(syminfo.tickerid, 'M', close[2], barmerge.gaps_off, barmerge.lookahead_on)
    c4803 = request.security(syminfo.tickerid, 'M', close[3], barmerge.gaps_off, barmerge.lookahead_on)
    c4804 = request.security(syminfo.tickerid, 'M', close[4], barmerge.gaps_off, barmerge.lookahead_on)
    c4805 = request.security(syminfo.tickerid, 'M', close[5], barmerge.gaps_off, barmerge.lookahead_on)
    h480 = request.security(syminfo.tickerid, '480', high, barmerge.gaps_off, barmerge.lookahead_on)
    mc = (c480 + c4801 + c4802 + c4803 + c4804) / 5
    plot(mc if TRAILING_MODE else na, 'TrailingTP/SL', color=color.new(color.lime, 0), style=plot.style_stepline, linewidth=2)
    prefillFast = plot(price1strategy if BG_MODE else na, 'Fast MA', color=color.new(color.red, 100), style=plot.style_line, linewidth=2)
    prefillMid = plot((price2strategy if BG_MODE else na) if MA2_MODE else na, 'Middle MA', color=color.new(color.blue, 100), style=plot.style_line, linewidth=2)
    prefillSlow = plot(price3strategy if BG_MODE else na, 'Fast MA', color=color.new(color.yellow, 100), style=plot.style_line, linewidth=2)
    fcolor = color.new(color.lime, 70) if price1strategy > price3strategy else color.new(color.blue, 70)
    fcolor2 = color.new(color.lime, 70) if price1strategy > price2strategy else color.new(color.red, 70)
    fill(prefillFast, prefillSlow, color=fcolor, title='BACKGROUND PAINT')
    fill(prefillFast, prefillMid, color=fcolor2, title='BACKGROUND PAINT')
    fuLi.NetProfit_Show(show_Net, position_, size_i, color_Net)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
