"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    alert, bar_index, barcolor, barstate, close, color, fill, high, input,
    location, low, math, na, open, plot, plotshape, request, script, shape, size, strategy,
    syminfo, ta, time, timeframe, timestamp
)
from pynecore.types import Persistent, Series


@script.strategy('3 Candle Strike Strategy', overlay=True, pyramiding=1, initial_capital=5000, margin_long=0, margin_short=0, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True)
def main(
    startY=input(title='Start Year', defval=2011, group='Trading window'),
    startM=input.int(title='Start Month', defval=1, minval=1, maxval=12, group='Trading window'),
    startD=input.int(title='Start Day', defval=1, minval=1, maxval=31, group='Trading window'),
    finishY=input(title='Finish Year', defval=2050, group='Trading window'),
    finishM=input.int(title='Finish Month', defval=12, minval=1, maxval=12, group='Trading window'),
    finishD=input.int(title='Finish Day', defval=31, minval=1, maxval=31, group='Trading window'),
    t1_session=input.session('0930-1554:23456', 'Entry Session', group='Sessions', tooltip='Entry Signal only generated within this period.'),
    margin_req=input.float(10, title='Margin Requirement / Leverage', step=0.1, group='Trading Options'),
    qty_per_trade=input.float(100, title='% of initial capital per trade', group='Trading Options'),
    reinvest=input.bool(defval=False, title='Reinvest profit', group='Trading Options'),
    reinvest_percent=input.float(defval=20, title='Reinvest percentage', group='Trading Options'),
    atrlen=input.int(14, minval=1, title='ATR period', group='Daily ATR'),
    iPercent=input.float(5, minval=1, maxval=100, step=0.1, title='% ATR to use for SL / PT', group='Daily ATR'),
    show_ema1=input.bool(False, '', group='Moving Averages', inline='ema1'),
    len0=input.int(8, minval=1, title='Fast EMA', group='Moving Averages', inline='ema1'),
    show_smma1=input.bool(False, '', group='Moving Averages', inline='smma1'),
    len1=input.int(21, minval=1, title='Fast SMMA', group='Moving Averages', inline='smma1'),
    show_smma2=input.bool(False, '', group='Moving Averages', inline='smma2'),
    len2=input.int(50, minval=1, title='Medium SMMA', group='Moving Averages', inline='smma2'),
    show_smma3=input.bool(False, '', group='Moving Averages', inline='smma3'),
    len3=input.int(200, minval=1, title='Slow SMMA', group='Moving Averages', inline='smma3'),
    clen=input.int(defval=50, minval=1, title='Linear Regression Period', group='Linear Regression'),
    slen=input.int(defval=50, minval=1, title='LR Slope Period', group='Linear Regression'),
    glen=input.int(defval=14, minval=1, title='LR Signal Period', group='Linear Regression'),
    LR_thres=input.float(0.03, minval=0, step=0.001, title='LR Threshold for Ranging vs Trending', group='Linear Regression'),
    RR=input.float(3.0, minval=0.1, step=0.1, title='Reward to Risk Ratio', group='Trading Options'),
    trade_trailing=input.bool(True, 'Switch to trailing SL after TP hit', group='Trading Options', tooltip='Set SL to previous low after TP hit'),
    no_entry=input.bool(True, title='No entry between:', group='Trading Options', inline='no_entry'),
    t2_session=input.session('1000-1030', '', group='Trading Options', inline='no_entry', tooltip='To avoid high volatility'),
    trade_3s=input.bool(title='Trade 3s candle pattern', defval=True, group='Trading Options', tooltip='Can use alert() function calls for all 3 Candle strike signals'),
    trade_ma_reversal=input.bool(title='Trade MA Cross Reversal Signal', defval=True, group='Trading Options')
):
    timestart = timestamp(startY, startM, startD, 0, 0)
    timefinish = timestamp(finishY, finishM, finishD, 23, 59)
    t1 = time(timeframe.period, t1_session)
    window = True if time >= timestart and time <= timefinish and cast_bool(t1) else False
    src = close
    profit = strategy.netprofit
    trade_amount = math.floor(strategy.initial_capital * margin_req / close)
    if strategy.netprofit > 0 and reinvest:
        trade_amount = math.floor((strategy.initial_capital * (qty_per_trade / 100) + profit * reinvest_percent * 0.01) * margin_req / close)
    else:
        trade_amount = math.floor(strategy.initial_capital * (qty_per_trade / 100) * margin_req / close)
    trade_amount = math.min(trade_amount, 1000)
    percentage = iPercent * 0.01
    datr = request.security(syminfo.tickerid, '1D', ta.rma(ta.tr, atrlen))
    datrp = datr * percentage
    plot(datr, 'Daily ATR')
    plot(datrp, 'Daily % ATR')
    ema1 = ta.ema(src, len0)
    smma1: Series[float] = 0.0
    sma_1 = ta.sma(src, len1)
    smma1 = sma_1 if na(smma1[1]) else (smma1[1] * (len1 - 1) + src) / len1
    smma2: Series[float] = 0.0
    sma_2 = ta.sma(src, len2)
    smma2 = sma_2 if na(smma2[1]) else (smma2[1] * (len2 - 1) + src) / len2
    smma3: Series[float] = 0.0
    sma_3 = ta.sma(src, len3)
    smma3 = sma_3 if na(smma3[1]) else (smma3[1] * (len3 - 1) + src) / len3
    ma_bull = smma1 > smma2 and smma1 > smma1[1]
    ma_bear = smma1 < smma2 and smma1 < smma1[1]
    ma_bull_macro = smma1 > smma3 and smma2 > smma3
    ma_bear_macro = smma1 < smma3 and smma2 < smma3
    plot(ema1 if show_ema1 else na, 'Fast EMA', color.white, linewidth=2)
    plot(smma1 if show_smma1 else na, 'Fast SMMA', color.yellow, linewidth=2)
    plot(smma2 if show_smma2 else na, 'Medium SMMA', color.orange, linewidth=2)
    plot(smma3 if show_smma3 else na, 'Fast SMMA', color.red, linewidth=2)
    lrc: Series = ta.linreg(src, clen, 0)
    lrs = (lrc - lrc[1]) / 1
    slrs = ta.ema(lrs, slen)
    alrs = ta.sma(slrs, glen)
    up_accel = lrs > alrs and lrs > 0
    down_accel = lrs < alrs and lrs < 0
    LR_ranging = math.abs(slrs) <= LR_thres
    LR_trending = math.abs(slrs) > LR_thres
    barcolor(color.gray if LR_ranging else na, title='Ranging')
    bull_3s = close[3] <= open[3] and close[2] <= open[2] and (close[1] <= open[1]) and (close > open[1])
    bear_3s = close[3] >= open[3] and close[2] >= open[2] and (close[1] >= open[1]) and (close < open[1])
    plotshape(bull_3s, style=shape.triangleup, color=color.new(color.green, 0), location=location.belowbar, size=size.small, text='3s-Bull', title='3 Line Strike Up')
    plotshape(bear_3s, style=shape.triangledown, color=color.new(color.red, 0), location=location.abovebar, size=size.small, text='3s-Bear', title='3 Line Strike Down')
    if barstate.isconfirmed:
        if bull_3s:
            alert(message='3s Bull')
        if bear_3s:
            alert(message='3s Bear')
    def barsSinceLastEntry():
        return bar_index - strategy.opentrades.entry_bar_index(strategy.opentrades - 1) if strategy.opentrades > 0 else na

    last_high = math.max(high, high[1], high[2], high[3])
    last_low = math.min(low, low[1], low[2], low[3])
    long_SL: Series = last_low - datrp
    short_SL: Series = last_high + datrp
    long_PT = last_high
    short_PT = last_low
    last_entry = strategy.opentrades.entry_price(strategy.opentrades - 1)
    risk = last_entry - long_SL
    if strategy.opentrades > 0:
        long_SL = math.min(long_SL[barsSinceLastEntry()], last_low)
        short_SL = math.max(short_SL[barsSinceLastEntry()], last_high)
        risk = last_entry - long_SL
        long_PT = last_entry + (last_entry - long_SL) * RR
        short_PT = last_entry - (short_SL - last_entry) * RR
    PT_hit: Persistent[bool] = False
    if trade_trailing:
        if high > long_PT:
            long_SL = low
            PT_hit = True
        if low < short_PT:
            short_SL = high
            PT_hit = True
        if PT_hit:
            long_SL = math.max(low[1], long_SL[1])
            short_SL = math.min(high[1], short_SL[1])
    PT_hit = False if strategy.opentrades == 0 else PT_hit
    barsSinceLastEntry_1 = barsSinceLastEntry()
    SSL = plot(short_SL, title='Short SL', color=color.red if strategy.opentrades.size(0) < 0 and barsSinceLastEntry_1 > 0 else na, linewidth=3, style=plot.style_linebr)
    barsSinceLastEntry_2 = barsSinceLastEntry()
    LSL = plot(long_SL, title='Long SL', color=color.red if strategy.opentrades.size(0) > 0 and barsSinceLastEntry_2 > 0 else na, linewidth=3, style=plot.style_linebr)
    barsSinceLastEntry_3 = barsSinceLastEntry()
    LPT = plot(long_PT, title='Long PT', color=color.green if strategy.opentrades.size(0) > 0 and barsSinceLastEntry_3 > 0 else na, linewidth=3, style=plot.style_linebr)
    barsSinceLastEntry_4 = barsSinceLastEntry()
    SPT = plot(short_PT, title='Short PT', color=color.green if strategy.opentrades.size(0) < 0 and barsSinceLastEntry_4 > 0 else na, linewidth=3, style=plot.style_linebr)
    LE = plot(last_entry, title='Last entry', color=color.gray if strategy.opentrades > 0 else na, style=plot.style_linebr)
    plot(risk, title='Risk')
    fill(LPT, LE, color=color.new(color.green, 90) if strategy.opentrades.size(0) > 0 else na)
    fill(LE, LSL, color=color.new(color.red, 90) if strategy.opentrades.size(0) > 0 else na)
    fill(SPT, LE, color=color.new(color.green, 90) if strategy.opentrades.size(0) < 0 else na)
    fill(LE, SSL, color=color.new(color.red, 90) if strategy.opentrades.size(0) < 0 else na)
    trade_pause: bool = False
    trade_pause2: bool = False
    t2 = time(timeframe.period, t2_session)
    if high - low > datr * 0.3:
        trade_pause = True
    else:
        trade_pause = False
    if no_entry and cast_bool(t2):
        trade_pause2 = True
    else:
        trade_pause2 = False
    L_entry1 = trade_3s and bull_3s and ma_bull and LR_trending
    S_entry1 = trade_3s and bear_3s and ma_bear and LR_trending
    cross_1 = ta.cross(ema1, smma1)
    barssince_1 = ta.barssince(cross_1)
    L_entry2 = trade_ma_reversal and ma_bear_macro and (ema1 > smma1) and bull_3s and (barssince_1 < 10)
    cross_2 = ta.cross(ema1, smma1)
    barssince_2 = ta.barssince(cross_2)
    S_entry2 = trade_ma_reversal and ma_bull_macro and (ema1 < smma1) and bear_3s and (barssince_2 < 10)
    L_exit1 = bear_3s
    S_exit1 = bull_3s
    if not trade_pause and (not trade_pause2) and window:
        if L_entry1:
            strategy.entry('Long', strategy.long, trade_amount, comment='Long 3s')
        if L_entry2:
            strategy.entry('Long', strategy.long, trade_amount, comment='Long MA cross')
        if S_entry1:
            strategy.entry('Short', strategy.short, trade_amount, comment='Short 3s')
        if S_entry2:
            strategy.entry('Short', strategy.short, trade_amount, comment='Short MA corss')
    if trade_trailing:
        strategy.exit('Exit', 'Long', stop=long_SL, comment='Exit Long SL hit')
        strategy.exit('Exit', 'Short', stop=short_SL, comment='Exit Short SL hit')
    elif barsSinceLastEntry() > 0:
        strategy.exit('Exit', 'Long', limit=long_PT, stop=long_SL, comment_profit='Exit Long PT hit', comment_loss='Exit Long SL hit')
        strategy.exit('Exit', 'Short', limit=short_PT, stop=short_SL, comment_profit='Exit Short PT hit', comment_loss='Exit Short SL hit')
    if strategy.opentrades > 0 and (not t1):
        strategy.close_all(comment='End of day')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
