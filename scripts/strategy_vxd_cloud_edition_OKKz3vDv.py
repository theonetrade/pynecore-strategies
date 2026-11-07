"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    barcolor, close, color, currency, fill, high, input, low, math, na, nz,
    open, plot, script, strategy, string, ta, time, timestamp, volume
)
from pynecore.types import Persistent, PersistentSeries, Series
import lib.Naruephat.Cayoshi_Library.v1 as fuLi

BTR1: str = '════════ INPUT BACKTEST TIME RANGE ════════'
cond0: str = 'Break Cloud + Pivot'
cond1: str = 'Break Cloud + Pivot + Subhag Filter'
cond2: str = 'Cloud-MA(New)'


@script.strategy('VXD Cloud', 'VXD', overlay=True, initial_capital=100, currency=currency.USD, pyramiding=1, process_orders_on_close=True, calc_on_every_tick=False, margin_long=0, margin_short=0, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True)
def main(
    i_startTime=input.time(defval=timestamp('01 Jan 1945 00:00 +0000'), title='Start', inline='timestart', group=BTR1),
    i_endTime=input.time(defval=timestamp('01 Jan 2074 23:59 +0000'), title='End', inline='timeend', group=BTR1),
    leverage=input.bool(title='Use Leverage?', defval=True, group='═ Strategy Setting ═', tooltip='If use "Position size" can be larger than Equity'),
    riskPer=input.int(10, 'Risk', minval=1, group='═ Strategy Setting ═', tooltip='Lost per trade', inline='risk'),
    risktype=input.string('$', '', options=('$', '%'), group='═ Strategy Setting ═', inline='risk'),
    conditype=input.string(cond2, 'Order Condition', options=(cond0, cond1, cond2), group='═ Strategy Setting ═'),
    uselong=input.bool(title='Open Buy?', defval=True, group='═ Strategy Setting ═'),
    useshort=input.bool(title='Open Sell?', defval=True, group='═ Strategy Setting ═'),
    useSL=input.bool(title='Use Take Profit/StopLoss?', defval=True, group='═ Strategy Setting ═', inline='Set'),
    useSLbox=input.bool(title='Show Profit/StopLoss Box?', defval=False, group='═ Strategy Setting ═'),
    useSLcl=input.color(defval=color.new(color.orange, 0), title='Color', inline='Set', group='═ Strategy Setting ═'),
    rrPer=input.float(3.0, 'Risk:Reward TP1', minval=1, step=0.1, group='═ Strategy Setting ═', inline='rr'),
    rrPer2=input.float(4.0, 'TP2', minval=1, step=0.1, group='═ Strategy Setting ═', inline='rr'),
    TPper=input.int(50, 'Equity % Take Profit TP1', minval=0, maxval=100, step=5, group='═ Strategy Setting ═', tooltip='Take a snack and let profit run.', inline='tp%'),
    TPper2=input.int(100, 'TP2', minval=0, maxval=100, step=5, group='═ Strategy Setting ═', inline='tp%'),
    Periods=input.int(title='ATR Period', defval=12, group='═ ATR Setting ═'),
    Multiplier=input.float(title='ATR Multiplier', step=0.1, defval=1.6, group='═ ATR Setting ═'),
    LengthRSI=input.int(25, 'RSI', minval=1, group='═ RSI Setting ═'),
    LengthAO=input.int(30, 'Length', minval=1, group='═ Andean Oscillator Setting ═'),
    LengthMA=input.int(30, 'EMA fast', minval=1, group='═ MA Setting ═', tooltip='Act as Trend line'),
    sma2cl=input.color(defval=color.new(color.purple, 0), title='EMA Slow', group='═ MA Setting ═', inline='sma200'),
    LengthMA2=input.int(200, 'Period', minval=1, group='═ MA Setting ═', inline='sma200'),
    length=input.int(30, minval=1, group='═ Subhag Setting ═'),
    smoothing=input.int(30, minval=1, group='═ Subhag Setting ═'),
    plotPVT=input.bool(defval=True, title='Plot Pivots', group='═ Pivots ═'),
    pivotLookup=input.int(defval=5, minval=1, maxval=8, title='Pivot Lookup', group='═ Pivots ═', tooltip='Minimum = 1, Maximum = 8'),
    pivotsizing=input.int(defval=50, minval=1, maxval=100, title='Pivot bars back for sizing', group='═ Pivots ═', tooltip='Minimum = 1, Maximum = 100'),
    plotInThePast=input(False, 'Plot When Pivot is Detected', group='═ Pivots ═'),
    pvtTopColor=input.color(defval=color.new(color.new('#76B579'), 10), title='Pivot Top Color', group='═ Pivots ═', inline='PVT Top Color'),
    pvtBottomColor=input.color(defval=color.new(color.new('#D85884'), 10), title='Pivot Bottom Color', group='═ Pivots ═', inline='PVT Top Color'),
    plotHVB=input.bool(defval=True, title='Plot HVB', group='═ High Volume Bar ═', tooltip='A candle where the average volume is higher than last few bars.'),
    hvbBullColor=input.color(defval=color.new(color.green, 0), title='Bullish HVB Color', inline='Set Custom Color', group='═ High Volume Bar ═'),
    hvbBearColor=input.color(defval=color.new(color.orange, 0), title='Bearish HVB Color', inline='Set Custom Color', group='═ High Volume Bar ═'),
    hvbEMAPeriod=input.int(defval=6, minval=1, title='Volume EMA Period', group='═ High Volume Bar ═'),
    hvbMultiplier=input.float(defval=1.2, title='Volume Multiplier', minval=1, maxval=100, group='═ High Volume Bar ═'),
    showcloud=input.bool(title='Show Cloud?', defval=True, group='═ Cloud Setting ═'),
    clhicl=input.color(defval=color.new(color.green, 100), title='Cloud High Color', group='═ Cloud Setting ═'),
    cllocl=input.color(defval=color.new(color.red, 100), title='Cloud Low Color', group='═ Cloud Setting ═'),
    clbgclbull=input.color(defval=color.green, title='Bull Cloud  Color', group='═ Cloud Setting ═'),
    clbgclbear=input.color(defval=color.red, title='Bear Cloud  Color', group='═ Cloud Setting ═'),
    clbgclsway=input.color(defval=color.yellow, title='Sideway Cloud  Color', group='═ Cloud Setting ═'),
    cltranpl=input.int(defval=80, title='Cloud  transparent', group='═ Cloud Setting ═'),
    show_Net=input.bool(True, 'Show Net', inline='Lnet'),
    position_=input.string('top_right', 'Position', options=('top_right', 'middle_right', 'bottom_right', 'top_center', 'middle_center', 'bottom_center', 'middle_left', 'bottom_left'), inline='Lnet'),
    size_i=input.string('normal', 'size', options=('auto', 'tiny', 'small', 'normal'), inline='Lnet'),
    color_Net=input.color(color.blue, '', inline='Lnet')
):
    timeCond = time > i_startTime and time < i_endTime
    ATR = ta.sma(ta.tr, Periods)
    downT = high + ATR * Multiplier
    upT = low - ATR * Multiplier
    supertrend, direction = ta.supertrend(Multiplier, Periods)
    rsibb = ta.rsi(close, LengthRSI)
    alpha: Persistent = 2 / (LengthAO + 1)
    up1: PersistentSeries[float] = 0.0
    up2: PersistentSeries[float] = 0.0
    dn1: PersistentSeries[float] = 0.0
    dn2: PersistentSeries[float] = 0.0
    C = close
    O = open
    up1 = nz(math.max(C, O, up1[1] - (up1[1] - C) * alpha), C)
    up2 = nz(math.max(C * C, O * O, up2[1] - (up2[1] - C * C) * alpha), C * C)
    dn1 = nz(math.min(C, O, dn1[1] + (C - dn1[1]) * alpha), C)
    dn2 = nz(math.min(C * C, O * O, dn2[1] + (C * C - dn2[1]) * alpha), C * C)
    bull = math.sqrt(dn2 - dn1 * dn1)
    bear = math.sqrt(up2 - up1 * up1)
    MA_1: float = ta.ema(close, LengthMA)
    MA_2 = ta.ema(close, LengthMA2)
    linreg = ta.ema(ta.linreg(close, length, 0), smoothing)
    isUplinreg = ta.rising(linreg, 2)
    isDnlinreg = ta.falling(linreg, 2)
    hullColor = color.green if isUplinreg else color.red if isDnlinreg else color.yellow
    AlphaTrend: Series[float] = 0.0
    CloudMA: Series[float] = 0.0
    cloudtrend: Series[int] = 0
    zonecl: Series = color.white
    ATcl: Series = color.new(color.yellow, 0)
    AlphaTrend = ((nz(AlphaTrend[1]) if upT < nz(AlphaTrend[1]) else upT) if rsibb >= 50 else nz(AlphaTrend[1]) if downT > nz(AlphaTrend[1]) else downT) if conditype == cond2 else supertrend
    fastl = ta.ema(close, 2)
    clohi = math.max(MA_1, linreg, AlphaTrend[2])
    clolo = math.min(MA_1, linreg, AlphaTrend[2])
    greenzone = close > clohi
    redzone = close < clolo
    greenzoneB = close > clohi and isUplinreg
    redzoneB = close < clolo and isDnlinreg
    CloudMA = (nz(CloudMA[1]) if clolo < nz(CloudMA[1]) else clolo) if bull > bear else (nz(CloudMA[1]) if clohi > nz(CloudMA[1]) else clohi) if bear > bull else nz(CloudMA[1])
    ATisup = ta.rising(CloudMA, 2)
    ATisdn = ta.falling(CloudMA, 2)
    cloudtrend = 1 if ATisup else -1 if ATisdn else cloudtrend[1]
    ATcl = clbgclbull if ATisup else clbgclbear if ATisdn else clbgclsway if CloudMA[1] == CloudMA else ATcl[1]
    kline = plot(CloudMA, color=color.new(ATcl, 0), linewidth=2)
    zonecl = color.new(clbgclbull, cltranpl) if greenzoneB and conditype == cond1 else color.new(clbgclbear, cltranpl) if redzoneB and conditype == cond1 else color.new(clbgclbull, cltranpl) if greenzone and conditype == cond0 else color.new(clbgclbear, cltranpl) if redzone and conditype == cond0 else color.new(ATcl, cltranpl) if conditype == cond2 else zonecl[1]
    main1 = plot(clohi, title='Cloud High', color=clhicl, linewidth=1)
    main2 = plot(clolo, title='Cloud low', color=cllocl, linewidth=1)
    fill(main1, main2, zonecl if showcloud else na)
    main3 = plot(MA_2, title='SMA', color=sma2cl, linewidth=2)
    hih = ta.pivothigh(high, pivotLookup, pivotLookup)
    lol = ta.pivotlow(low, pivotLookup, pivotLookup)
    top: Series = ta.valuewhen(cast_bool(hih), high[pivotLookup], 0)
    bottom: Series = ta.valuewhen(cast_bool(lol), low[pivotLookup], 0)
    pvtop = plot(top, offset=0 if plotInThePast else -pivotLookup, linewidth=1, color=na if top != top[1] else pvtTopColor if plotPVT else na, title='Pivot Top')
    pvdow = plot(bottom, offset=0 if plotInThePast else -pivotLookup, linewidth=1, color=na if bottom != bottom[1] else pvtBottomColor if plotPVT else na, title='Pivot Bottom')
    volEma = ta.sma(volume, hvbEMAPeriod)
    isHighVolume = volume > hvbMultiplier * volEma
    def isUp(index):
        return close[index] > open[index]

    def isDown(index):
        return close[index] < open[index]

    isUp_1 = isUp(0)
    barcolor(hvbBullColor if plotHVB and isUp_1 and isHighVolume else na, title='Bullish HVB')
    isDown_1 = isDown(0)
    barcolor(hvbBearColor if plotHVB and isDown_1 and isHighVolume else na, title='Bearish HVB')
    position_size = strategy.position_size
    Eqty = strategy.equity
    lotsize: Series[float] = 0.0
    RR0: float = 0.0
    RR1: Series[float] = 0.0
    SLbuy: Series[float] = 0.0
    SLsell: Series[float] = 0.0
    openoncel = strategy.opentrades == 0 or position_size <= 0
    openonces = strategy.opentrades == 0 or position_size >= 0
    exitshort = cast_bool(ta.change(cloudtrend)) and cloudtrend == 1 if conditype == cond2 else close > clohi and close > top
    exitlong = cast_bool(ta.change(cloudtrend)) and cloudtrend == -1 if conditype == cond2 else close < clolo and close < bottom
    highest = ta.highest(top, pivotsizing)
    lowest = ta.lowest(bottom, pivotsizing)
    percentrisk = riskPer / 100 * Eqty if risktype == '%' else riskPer
    LongCondition = openoncel and close > top and greenzone and timeCond
    LongConditionB = openoncel and close > top and greenzoneB and timeCond
    ShortCondition = openonces and close < bottom and redzone and timeCond
    ShortConditionB = openonces and close < bottom and redzoneB and timeCond
    LongConditionC = cloudtrend > 0 and openoncel and greenzone and timeCond
    ShortConditionC = cloudtrend < 0 and openonces and redzone and timeCond
    actionbull = LongConditionB if conditype == cond1 else LongCondition if conditype == cond0 else LongConditionC if conditype == cond2 else False
    actionbear = ShortConditionB if conditype == cond1 else ShortCondition if conditype == cond0 else ShortConditionC if conditype == cond2 else False
    changetbull = ta.change(actionbull)
    changetbear = ta.change(actionbear)
    buyprice: Series[float] = 0.0
    sellprice: Series[float] = 0.0
    mapast: float = 0.0
    openprice = strategy.opentrades.entry_price(0)
    TPbear: Series[float] = 0.0
    TPbull: Series[float] = 0.0
    onebuy: Series[int] = 0
    onesell: Series[int] = 0
    TPbull2: Series[float] = 0.0
    TPbear2: Series[float] = 0.0
    stat_H: Series[float] = 0.0
    stat_L: Series[float] = 0.0
    lotsize = math.abs(percentrisk / (close - lowest)) if changetbull else math.abs(percentrisk / (highest - close)) if changetbear else lotsize[1]
    while not leverage and lotsize * close > Eqty:
        lotsize = lotsize / 2
    buyprice = (openprice if changetbull else buyprice[1]) if position_size >= 0 else na
    sellprice = (openprice if changetbear else sellprice[1]) if position_size <= 0 else na
    RR1 = buyprice * (1 + (openprice - lowest) / openprice * 1) if changetbull else sellprice * (1 - (highest - openprice) / openprice * 1) if changetbear else RR1[1]
    TPbull = buyprice * (1 + (openprice - lowest) / openprice * rrPer) if changetbull else TPbull[1] if position_size > 0 else 0.0 if position_size < 0 else 0.0
    TPbull2 = buyprice * (1 + (openprice - lowest) / openprice * rrPer2) if changetbull else TPbull2[1] if position_size > 0 else 0.0 if position_size < 0 else 0.0
    TPbear = sellprice * (1 - (highest - openprice) / openprice * rrPer) if changetbear else TPbear[1] if position_size < 0 else 0.0 if position_size > 0 else 0.0
    TPbear2 = sellprice * (1 - (highest - openprice) / openprice * rrPer2) if changetbear else TPbear2[1] if position_size < 0 else 0.0 if position_size > 0 else 0.0
    stat_H = (high if high > high[1] else stat_H[1]) if position_size != 0 else high
    stat_L = (low if low < low[1] else stat_L[1]) if position_size != 0 else low
    SLbuy = lowest if exitshort else buyprice if position_size > 0 and stat_H > RR1 else SLbuy[1]
    SLsell = highest if exitlong else sellprice if position_size < 0 and stat_L < RR1 else SLsell[1]
    isslbuy = ta.crossunder(stat_L, SLbuy)
    isslsell = ta.crossover(stat_H, SLsell)
    onebuy = 1 if cloudtrend[1] != 1 and cloudtrend == 1 else 0 if isslbuy else 1 if position_size > 0 else 0 if cloudtrend == -1 else onebuy[1]
    onesell = 1 if cloudtrend[1] != -1 and cloudtrend == -1 else 0 if isslsell else 1 if position_size < 0 else 0 if cloudtrend == 1 else onesell[1]
    linetp = plot((TPbull if useSL and position_size > 0 else TPbear if useSL and position_size < 0 else na) if useSLbox else TPbull if useSL and changetbull else TPbear if useSL and changetbear else na, 'TP', color.green if useSLbox else useSLcl, style=plot.style_linebr, linewidth=1)
    linetp2 = plot((TPbull2 if useSL and position_size > 0 else TPbear2 if useSL and position_size < 0 else na) if useSLbox else TPbull2 if useSL and changetbull else TPbear2 if useSL and changetbear else na, 'TP2', color.green if useSLbox else useSLcl, style=plot.style_linebr, linewidth=1)
    lintsl = plot((SLbuy if useSL and position_size > 0 else SLsell if useSL and position_size < 0 else na) if useSLbox else SLbuy if useSL and changetbull else SLsell if useSL and changetbear else na, 'SL', color.red if useSLbox else useSLcl, style=plot.style_linebr, linewidth=1)
    lineentry = plot(buyprice if useSLbox and position_size > 0 else sellprice if useSLbox and position_size < 0 else na, 'Entry', color.white, style=plot.style_linebr, linewidth=1)
    fill(lineentry, linetp2, color.new(color.green, 80))
    fill(lineentry, lintsl, color.new(color.red, 80))
    Alert_OpenLong: str = 'Long Entry! on {{ticker}} \n Buy@ {{strategy.order.price}} \n Size = {{strategy.order.contracts}} \n SL @ ' + string.tostring(SLbuy)
    Alert_OpenShort: str = 'Short Entry! on {{ticker}} \n Sell@ {{strategy.order.price}} \n Size = {{strategy.order.contracts}} \n SL @ ' + string.tostring(SLsell)
    Alert_LongTP: str = 'TP/SL Long on {{ticker}} \n @ {{strategy.order.price}} \n Size = {{strategy.order.contracts}}'
    Alert_ShortTP: str = 'TP/SL Short on {{ticker}} \n @ {{strategy.order.price}} \n Size = {{strategy.order.contracts}}'
    message_closelong: Persistent[str] = 'Tailing Stop Long!!! on {{ticker}} \n @ {{strategy.order.price}}'
    message_closeshort: Persistent[str] = 'Tailing Stop Short!!! on {{ticker}} \n @ {{strategy.order.price}}'
    Alert_StopLosslong: str = 'StopLoss Long! on {{ticker}} \n @ {{strategy.order.price}}'
    Alert_StopLossshort: str = 'StopLoss Short! on {{ticker}} \n @ {{strategy.order.price}}'
    if exitlong == True:
        strategy.close('long2', comment='TailingStop-L', alert_message=message_closelong)
    if exitshort == True:
        strategy.close('Short2', comment='TailingStop-S', alert_message=message_closeshort)
    if uselong == True and changetbull and (onebuy[1] == 0):
        strategy.entry('long2', strategy.long, qty=lotsize, comment='Long', alert_message=Alert_OpenLong)
    if useshort == True and changetbear and (onesell[1] == 0):
        strategy.entry('Short2', strategy.short, qty=lotsize, comment='Short', alert_message=Alert_OpenShort)
    if position_size > 0 and useSL:
        strategy.exit('TP1', 'long2', comment='SL/TP1', limit=TPbull, alert_message=Alert_LongTP, qty_percent=TPper, stop=SLbuy)
        strategy.exit('TP2', 'long2', comment='SL/TP2', limit=TPbull2, alert_message=Alert_LongTP, qty_percent=TPper2, stop=SLbuy)
        strategy.exit('SL', 'long2', comment='SL', stop=SLbuy, alert_message=Alert_StopLosslong)
    if position_size < 0 and useSL:
        strategy.exit('STP1', 'Short2', comment='SL/TP1', limit=TPbear, alert_message=Alert_ShortTP, qty_percent=TPper, stop=SLsell)
        strategy.exit('STP2', 'Short2', comment='SL/TP2', limit=TPbear2, alert_message=Alert_ShortTP, qty_percent=TPper2, stop=SLsell)
        strategy.exit('SSL', 'Short2', comment='SL', stop=SLsell, alert_message=Alert_StopLossshort)
    fuLi.NetProfit_Show(show_Net, position_, size_i, color_Net)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
