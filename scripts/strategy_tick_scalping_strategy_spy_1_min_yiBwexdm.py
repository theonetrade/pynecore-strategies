"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    bar_index, barstate, bgcolor, close, color, high, hline, input, location,
    low, math, na, plot, plotshape, request, script, shape, size, strategy, syminfo, ta, time,
    timeframe, timestamp
)
from pynecore.types import Series


@script.strategy('TICK strategy, SPY 1 min', overlay=False, pyramiding=3, initial_capital=5000, commission_type=strategy.commission.cash_per_contract, commission_value=0.0625, margin_long=0, margin_short=0, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    indicator_only=input.bool(False, 'Use As Indicator Only', tooltip='Disables strategy signals'),
    startY=input(title='Start Year', defval=2011, group='Trading window'),
    startM=input.int(title='Start Month', defval=1, minval=1, maxval=12, group='Trading window'),
    startD=input.int(title='Start Day', defval=1, minval=1, maxval=31, group='Trading window'),
    finishY=input(title='Finish Year', defval=2050, group='Trading window'),
    finishM=input.int(title='Finish Month', defval=12, minval=1, maxval=12, group='Trading window'),
    finishD=input.int(title='Finish Day', defval=31, minval=1, maxval=31, group='Trading window'),
    trade_options=input.bool(defval=True, title='Trading Options only', group='Trading Options'),
    option_amt=input.int(defval=10, title='# of options per trade', group='Trading Options'),
    option_multiplier=input.float(0.007, title='Multiplier for trading options (adjust to approx. options P&L)', step=0.001, group='Trading Options'),
    reinvest=input.bool(defval=False, title='Reinvest profit', group='Trading Options'),
    reinvest_percent=input.float(defval=20, title='Reinvest percentage', group='Trading Options'),
    trade_TICKdiverg=input.bool(True, title='Trade with TICK divergences', group='Trading Options'),
    diverg_lookback=input.int(defval=5, title='TICK divergence lookback period (only if trading TICK divergence', group='Trading Options'),
    trade_optimal=input.bool(True, title='Trade with optimal Stochastic', group='Trading Options'),
    entry_lookback=input.int(defval=12, title='Lookback period for entry condition, waiting for Stochastic', group='Trading Options'),
    k_entry_thres=input.int(defval=0, title='Stochastic RSI k value offset from 50 for entry threshold (ie. 10 means long entry under k=60', group='Trading Options'),
    trade_chase=input.bool(True, title='Trade with Chasing entries', group='Trading Options'),
    chase_lookback=input.int(defval=10, title='Chase entry lookback period', group='Trading Options'),
    k_chase_thres=input.int(defval=30, title='Stochastic RSI k value offset from 50 for chase entry threshold (ie. 30 means long entry under k=80', group='Trading Options'),
    trade_PT=input.bool(True, title='Trade with Price Target', group='Trading Options'),
    no_longat10=input.bool(False, title='No entry between 10 - 10:30', group='Trading Options'),
    hold_ON=input.bool(True, title='Hold 1/2 position overnight on Tues/Thurs', group='Trading Options'),
    atrlen=input.int(4, minval=1, title='ATR period', group='Daily ATR'),
    SL_atr_perc=input.float(9, minval=1, maxval=100, step=0.5, title='% ATR to use for SL', group='Daily ATR'),
    PT_atr_perc=input.float(17.5, minval=1, maxval=100, step=0.5, title='% ATR to use for PT (only if trading w/ PT)', group='Daily ATR'),
    vix_thres=input.float(20.0, 'VIX Threshold for entry', step=0.5, group='VIX Volatility Index'),
    malen1=input.int(21, title='Fast EMA period', group='TICK Indicator'),
    malen2=input.int(102, title='Slow EMA period', group='TICK Indicator'),
    malen3=input.int(135, title='Hull MA period', group='TICK Indicator'),
    malen4=input.int(25, title='Hull MA Smoothing', group='TICK Indicator'),
    lbR=input(title='Pivot Lookback Right', defval=5, group='TICK Divergence'),
    lbL=input(title='Pivot Lookback Left', defval=10, group='TICK Divergence'),
    rangeUpper=input(title='Max of Lookback Range', defval=300, group='TICK Divergence'),
    rangeLower=input(title='Min of Lookback Range', defval=25, group='TICK Divergence'),
    plotBull=input(title='Plot Bullish', defval=True, group='TICK Divergence'),
    plotHiddenBull=input(title='Plot Hidden Bullish', defval=False, group='TICK Divergence'),
    plotBear=input(title='Plot Bearish', defval=True, group='TICK Divergence'),
    plotHiddenBear=input(title='Plot Hidden Bearish', defval=False, group='TICK Divergence'),
    rsi_len=input.int(70, minval=1, title='RSI Length', group='RSI'),
    rsi_ma_len=input.int(6, minval=1, title='RSI Signal Length', group='RSI'),
    rsi_thres=input.int(15, 'RSI Overbought/Oversold levels +/- from 50', group='RSI'),
    rsi_len2=input.int(14, minval=1, title='Fast RSI Length', group='RSI'),
    smoothK=input.int(3, minval=1, title='Stoch K', group='Stochastic RSI'),
    smoothD=input.int(3, minval=1, title='Stoch D', group='Stochastic RSI'),
    lengthRSI=input.int(14, 'RSI Length', minval=1, group='Stochastic RSI'),
    lengthStoch=input.int(14, 'Stochastic Length', minval=1, group='Stochastic RSI'),
    emalen1=input.int(20, minval=1, title='Filtering EMA', group='Moving Averages'),
    min_hold=input.int(6, 'Minimum bars to hold order', group='Trading Options')
):
    timestart = timestamp(startY, startM, startD, 0, 0)
    timefinish = timestamp(finishY, finishM, finishD, 23, 59)
    t1 = time(timeframe.period, '0930-1545:23456')
    window = True if time >= timestart and time <= timefinish and cast_bool(t1) else False
    t2 = time(timeframe.period, '0930-1555:23456')
    window2 = True if time >= timestart and time <= timefinish and cast_bool(t2) else False
    SL_atr = SL_atr_perc * 0.01
    PT_atr = PT_atr_perc * 0.01
    datr = request.security(syminfo.tickerid, '1D', ta.rma(ta.tr, atrlen))
    d_SL_atr = datr * SL_atr
    d_PT_atr = datr * PT_atr
    VIX = request.security('VIX', timeframe.period, close)
    tickH = request.security('USI:TICK', '5', high)
    tickC: Series = request.security('USI:TICK', '5', close)
    tickL = request.security('USI:TICK', '5', low)
    tickAVG: Series = ta.ema(tickC, malen1)
    tickAVG_L = ta.ema(tickC, malen2)
    def f_hma(_src, _length):
        _return = ta.wma(2 * ta.wma(_src, _length / 2) - ta.wma(_src, _length), math.round(math.sqrt(_length)))
        return _return

    tickHMA: Series = f_hma(tickC, malen3)
    tickHMA_MA = ta.sma(tickHMA, malen4)
    tick_bull = tickAVG > tickAVG[5]
    tick_bear = tickAVG < tickAVG[5]
    plot(tickC if barstate.isconfirmed else na, title='TICK', color=color.new(color.white, 30), style=plot.style_line, linewidth=1)
    plot(tickAVG, title='TICK 9 EMA', color=color.yellow, style=plot.style_line, linewidth=1)
    plot(tickAVG_L, title='TICK 21 EMA', color=color.new(color.red, 70), style=plot.style_line, linewidth=1)
    plot(tickHMA, title='TICK 21 HMA', color=color.blue, style=plot.style_line, linewidth=2)
    plot(tickHMA_MA, title='TICK HMA Smoothed', color=color.purple, style=plot.style_line, linewidth=2)
    hline(0, color=color.white, linewidth=1, linestyle=hline.style_solid)
    hline(1000, color=color.green, linestyle=hline.style_solid, linewidth=2)
    hline(500, color=color.gray, linestyle=hline.style_dashed)
    hline(-1000, color=color.red, linestyle=hline.style_solid, linewidth=2)
    hline(-500, color=color.gray, linestyle=hline.style_dashed)
    plotshape(ta.crossunder(tickHMA, tickHMA_MA), 'Cross down', color=color.red, style=shape.triangledown, location=location.top, size=size.tiny)
    plotshape(ta.crossover(tickHMA, tickHMA_MA), 'Cross up', color=color.green, style=shape.triangleup, location=location.bottom, size=size.tiny)
    bgcolor(color.new(color.green, 90) if tickAVG_L > 0 else color.new(color.red, 90))
    bgcolor(color.new(color.green, 70) if tickC > 499 else na)
    bgcolor(color.new(color.red, 70) if tickC < -499 else na)
    bgcolor(color.new(color.green, 30) if tickC > 999 else na)
    bgcolor(color.new(color.red, 30) if tickC < -999 else na)
    bearColor = color.red
    bullColor = color.green
    hiddenBullColor = color.new(color.green, 80)
    hiddenBearColor = color.new(color.red, 80)
    textColor = color.white
    noneColor = color.new(color.white, 100)
    plFound: Series = False if na(ta.pivotlow(tickC, lbL, lbR)) else True
    phFound: Series = False if na(ta.pivothigh(tickC, lbL, lbR)) else True
    def _inRange(cond):
        bars = ta.barssince(cond == True)
        return rangeLower <= bars and bars <= rangeUpper

    _inRange_1 = _inRange(plFound[1])
    oscHL = tickC[lbR] > ta.valuewhen(plFound, tickC[lbR], 1) and _inRange_1
    priceLL = low[lbR] < ta.valuewhen(plFound, low[lbR], 1)
    bullCond = plotBull and priceLL and oscHL and plFound
    plot(tickC[lbR] if plFound else na, offset=-lbR, title='Regular Bullish', linewidth=2, color=bullColor if bullCond else noneColor)
    plotshape(tickC[lbR] if bullCond else na, offset=-lbR, title='Regular Bullish Label', text=' Bull ', style=shape.labelup, location=location.absolute, color=color.new(bullColor, 0), textcolor=color.new(textColor, 0))
    _inRange_2 = _inRange(plFound[1])
    oscLL = tickC[lbR] < ta.valuewhen(plFound, tickC[lbR], 1) and _inRange_2
    priceHL = low[lbR] > ta.valuewhen(plFound, low[lbR], 1)
    hiddenBullCond = plotHiddenBull and priceHL and oscLL and plFound
    plot(tickC[lbR] if plFound else na, offset=-lbR, title='Hidden Bullish', linewidth=2, color=hiddenBullColor if hiddenBullCond else noneColor)
    plotshape(tickC[lbR] if hiddenBullCond else na, offset=-lbR, title='Hidden Bullish Label', text=' H Bull ', style=shape.labelup, location=location.absolute, color=color.new(bullColor, 0), textcolor=color.new(textColor, 0))
    _inRange_3 = _inRange(phFound[1])
    oscLH = tickC[lbR] < ta.valuewhen(phFound, tickC[lbR], 1) and _inRange_3
    priceHH = high[lbR] > ta.valuewhen(phFound, high[lbR], 1)
    bearCond = plotBear and priceHH and oscLH and phFound
    plot(tickC[lbR] if phFound else na, offset=-lbR, title='Regular Bearish', linewidth=2, color=bearColor if bearCond else noneColor)
    plotshape(tickC[lbR] if bearCond else na, offset=-lbR, title='Regular Bearish Label', text=' Bear ', style=shape.labeldown, location=location.absolute, color=color.new(bearColor, 0), textcolor=color.new(textColor, 0))
    _inRange_4 = _inRange(phFound[1])
    oscHH = tickC[lbR] > ta.valuewhen(phFound, tickC[lbR], 1) and _inRange_4
    priceLH = high[lbR] < ta.valuewhen(phFound, high[lbR], 1)
    hiddenBearCond = plotHiddenBear and priceLH and oscHH and phFound
    plot(tickC[lbR] if phFound else na, offset=-lbR, title='Hidden Bearish', linewidth=2, color=hiddenBearColor if hiddenBearCond else noneColor)
    plotshape(tickC[lbR] if hiddenBearCond else na, offset=-lbR, title='Hidden Bearish Label', text=' H Bear ', style=shape.labeldown, location=location.absolute, color=color.new(bearColor, 0), textcolor=color.new(textColor, 0))
    src = close
    rsi_up = ta.rma(math.max(ta.change(src), 0), rsi_len)
    rsi_down = ta.rma(-math.min(ta.change(src), 0), rsi_len)
    rsi = 100 if rsi_down == 0 else 0 if rsi_up == 0 else 100 - 100 / (1 + rsi_up / rsi_down)
    rsi_ma = ta.wma(rsi, rsi_ma_len)
    rsi_avg: Series = rsi_ma
    rsi_bull = rsi_avg > rsi_avg[1]
    rsi_bear = rsi_avg < rsi_avg[1]
    rsi_up2 = ta.rma(math.max(ta.change(src), 0), rsi_len2)
    rsi_down2 = ta.rma(-math.min(ta.change(src), 0), rsi_len2)
    rsi2 = 100 if rsi_down2 == 0 else 0 if rsi_up2 == 0 else 100 - 100 / (1 + rsi_up2 / rsi_down2)
    rsi_stoch = ta.rsi(src, lengthRSI)
    k: Series = ta.sma(ta.stoch(rsi_stoch, rsi_stoch, rsi_stoch, lengthStoch), smoothK)
    d = ta.sma(k, smoothD)
    ma_src = close
    ema1 = ta.ema(ma_src, emalen1)
    profit = strategy.netprofit
    trade_amount = math.floor(strategy.initial_capital / close)
    def BSLE():
        return bar_index - strategy.opentrades.entry_bar_index(strategy.opentrades - 1) if strategy.opentrades > 0 else na

    def BSLExit():
        return bar_index - strategy.closedtrades.exit_bar_index(strategy.closedtrades - 1) if strategy.opentrades == 0 else na

    if trade_options:
        if strategy.netprofit > 0 and reinvest:
            trade_amount = math.floor(strategy.initial_capital * option_multiplier) * (option_amt + math.floor(profit * reinvest_percent * 0.01 / strategy.initial_capital * 10))
        else:
            trade_amount = math.floor(strategy.initial_capital * option_multiplier) * option_amt
    trade_pause: bool = False
    trade_pause2: bool = False
    trade_pause = False
    time_1 = time(timeframe.period, '1000-1030:23456')
    if no_longat10 and cast_bool(time_1):
        trade_pause2 = True
    else:
        trade_pause2 = False
    L_entry0 = ta.crossover(tickHMA, tickHMA_MA) and rsi_avg > 50 and (rsi < 50 + rsi_thres) and (VIX > vix_thres) and (tickAVG > 0) and (close > ema1)
    S_entry0 = ta.crossunder(tickHMA, tickHMA_MA) and rsi_avg < 50 and (rsi > 50 - rsi_thres) and (VIX > vix_thres) and (tickAVG < 0) and (close < ema1)
    L_entry1 = L_entry0
    S_entry1 = S_entry0
    BSL = ta.barssince(L_entry0)
    BSS = ta.barssince(S_entry0)
    if trade_optimal and strategy.opentrades == 0:
        if BSL < entry_lookback:
            L_entry1 = k < 50 + k_entry_thres and k > k[1]
        else:
            L_entry1 = L_entry0
        if BSS < entry_lookback:
            S_entry1 = k > 50 - k_entry_thres and k < k[1]
        else:
            S_entry1 = S_entry0
    L_entry2 = bullCond and tickHMA > tickHMA_MA and (rsi > rsi_ma) and (VIX > vix_thres) and (tickAVG > 0) and (close > ema1)
    S_entry2 = bearCond and tickHMA < tickHMA_MA and (rsi < rsi_ma) and (VIX > vix_thres) and (tickAVG < 0) and (close < ema1)
    BSLExit_1 = BSLExit()
    L_entry3 = BSLExit() < chase_lookback and close > close[BSLExit_1] and (tickHMA > tickHMA_MA) and (tickHMA > tickHMA[1]) and (rsi_avg > 50) and (rsi < 50 + rsi_thres) and (VIX > vix_thres) and (tickAVG > tickAVG[1]) and (close > ema1) and (k < 50 + k_chase_thres)
    BSLExit_2 = BSLExit()
    S_entry3 = BSLExit() < chase_lookback and close < close[BSLExit_2] and (tickHMA < tickHMA_MA) and (tickHMA < tickHMA[1]) and (rsi_avg < 50) and (rsi > 50 - rsi_thres) and (VIX > vix_thres) and (tickAVG < tickAVG[1]) and (close < ema1) and (k > 50 - k_chase_thres)
    if not indicator_only:
        if L_entry1 and window and (not trade_pause) and (not trade_pause2) and barstate.isconfirmed:
            strategy.entry('Long', strategy.long, trade_amount, comment='Long')
        if trade_TICKdiverg and L_entry2 and window and (not trade_pause) and (not trade_pause2) and barstate.isconfirmed and (strategy.opentrades == 0):
            strategy.entry('Long', strategy.long, trade_amount, comment='Long, TICK divergence')
        if trade_chase and L_entry3 and window and (not trade_pause) and (not trade_pause2) and barstate.isconfirmed and (strategy.opentrades == 0):
            strategy.entry('Long', strategy.long, trade_amount, comment='Long, Chase')
        if S_entry1 and window and (not trade_pause) and (not trade_pause2) and barstate.isconfirmed:
            strategy.entry('Short', strategy.short, trade_amount, comment='Short')
        if trade_TICKdiverg and S_entry2 and window and (not trade_pause) and (not trade_pause2) and barstate.isconfirmed and (strategy.opentrades == 0):
            strategy.entry('Short', strategy.short, trade_amount, comment='Short, TICK divergence')
        if trade_chase and S_entry3 and window and (not trade_pause) and (not trade_pause2) and barstate.isconfirmed and (strategy.opentrades == 0):
            strategy.entry('Short', strategy.short, trade_amount, comment='Short, Chase')
    long_SL: Series = ta.lowest(low, 5) - d_SL_atr
    short_SL: Series = ta.highest(high, 5) + d_SL_atr
    if strategy.opentrades > 0:
        long_SL = math.min(long_SL[BSLE()], low[1] - d_SL_atr)
        short_SL = math.max(short_SL[BSLE()], high[1] + d_SL_atr)
    long_PT = close + d_PT_atr
    short_PT = close - d_PT_atr
    if strategy.opentrades > 0:
        long_PT = strategy.opentrades.entry_price(0) + d_PT_atr
        short_PT = strategy.opentrades.entry_price(0) - d_PT_atr
    L_exit1 = tickHMA < tickHMA_MA and rsi_bear
    S_exit1 = tickHMA > tickHMA_MA and rsi_bull
    L_exit2 = bearCond
    S_exit2 = bullCond
    L_exit3 = tickH > 1000
    S_exit3 = tickL < -1000
    L_exit4 = strategy.opentrades.profit(strategy.opentrades - 1) > 0 and tickHMA < tickHMA[1] and (rsi2 < 50)
    S_exit4 = strategy.opentrades.profit(strategy.opentrades - 1) > 0 and tickHMA > tickHMA[1] and (rsi2 > 50)
    if BSLE() > min_hold and window2:
        if trade_PT:
            strategy.exit('Exit', 'Long', stop=long_SL, limit=long_PT, comment='SL/PT hit')
            strategy.exit('Exit', 'Short', stop=short_SL, limit=short_PT, comment='SL/PT hit')
        else:
            strategy.exit('Exit', 'Long', stop=long_SL, comment='SL hit')
            strategy.exit('Exit', 'Short', stop=short_SL, comment='SL hit')
        if L_exit1:
            strategy.close('Long', comment='Exit, TICK/RSI reversal')
        if S_exit1:
            strategy.close('Short', comment='Exit, TICK/RSI reversal')
        if L_exit2:
            strategy.close('Long', comment='Exit, Bearish Divergence')
        if S_exit2:
            strategy.close('Short', comment='Exit, Bullish Divergence')
        if L_exit3:
            strategy.close('Long', comment='Exit, TICK overbought')
        if S_exit3:
            strategy.close('Short', comment='Exit, TICK oversold')
    if hold_ON:
        if cast_bool(time(timeframe.period, '1550-1551:246')):
            strategy.close_all()
        if cast_bool(time(timeframe.period, '1550-1551:35')):
            strategy.close('Long', qty_percent=50, comment='Close 1/2 EOD')
            strategy.close('Short', qty_percent=50, comment='Close 1/2 EOD')
    else:
        if cast_bool(time(timeframe.period, '1550-1551:23456')):
            strategy.close_all()


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
