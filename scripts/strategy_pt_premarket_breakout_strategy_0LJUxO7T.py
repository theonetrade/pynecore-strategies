"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    bar_index, bgcolor, close, color, fill, high, input, low, math, na, plot,
    request, script, strategy, syminfo, ta, time, timeframe, timestamp
)
from pynecore.types import Persistent, Series

TT_stochLen: str = 'For 1 min time frame, use default 14.' + '\nFor 5 min time frame, use 3.'


@script.strategy('[Pt] Premarket Breakout Strategy', shorttitle='PM Break Strategy', overlay=True, pyramiding=1, initial_capital=4000, commission_type=strategy.commission.cash_per_contract, slippage=3, margin_long=0, margin_short=0, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True)
def main(
    startY=input(title='Start Year', defval=2011, group='Trading window'),
    startM=input.int(title='Start Month', defval=1, minval=1, maxval=12, group='Trading window'),
    startD=input.int(title='Start Day', defval=1, minval=1, maxval=31, group='Trading window'),
    finishY=input(title='Finish Year', defval=2050, group='Trading window'),
    finishM=input.int(title='Finish Month', defval=12, minval=1, maxval=12, group='Trading window'),
    finishD=input.int(title='Finish Day', defval=31, minval=1, maxval=31, group='Trading window'),
    t1_session=input.session('0945-1545', 'Entry Session', group='Sessions'),
    margin_req=input.float(11, title='Margin Requirement / Leverage', step=0.1, group='Trading Options'),
    reinvest=input.bool(defval=False, title='Reinvest profit', group='Trading Options'),
    reinvest_percent=input.float(defval=100, title='Reinvest percentage', group='Trading Options'),
    atrlen=input.int(14, minval=1, title='ATR period', group='Daily ATR'),
    iPercent=input.float(1.6, minval=0.01, maxval=100, step=0.2, title='% ATR to use for SL / PT', group='Daily ATR'),
    pm_session=input.session('0900-0930', 'Pre-Market Session', group='Sessions'),
    smoothK=input.int(3, 'K', minval=1, group='Stochastic RSI'),
    smoothD=input.int(3, 'D', minval=1, group='Stochastic RSI'),
    lengthRSI=input.int(14, 'RSI Length', minval=1, group='Stochastic RSI', tooltip=TT_stochLen),
    lengthStoch=input.int(14, 'Stochastic Length', minval=1, group='Stochastic RSI', tooltip=TT_stochLen),
    src: Series[float] = input(close, title='RSI Source'),
    len=input.int(14, minval=1, title='RSI Length', group='RSI Settings'),
    len2=input.int(3, title='Smooth period', group='RSI Settings'),
    maType=input.string('SMA', title='MA Type', options=('SMA', 'Bollinger Bands', 'EMA', 'SMMA (RMA)', 'WMA', 'VWMA'), group='RSI Settings'),
    malen=input.int(100, title='MA Length', group='RSI Settings'),
    stoch_h_limit=input.int(82, 'Stochastic K must be above before entry', group='Entry parameters'),
    stoch_l_limit=input.int(18, 'Stochastic K must be above before entry', group='Entry parameters'),
    RRR=input.float(2.0, 'Reward to Risk Ratio', step=0.1, group='Trading Options')
):
    timestart = timestamp(startY, startM, startD, 0, 0)
    timefinish = timestamp(finishY, finishM, finishD, 23, 59)
    t1 = time(timeframe.period, t1_session)
    window = True if time >= timestart and time <= timefinish and cast_bool(t1) else False
    profit = strategy.netprofit
    trade_amount = math.floor(strategy.initial_capital * margin_req / close)
    def BSLE():
        return bar_index - strategy.opentrades.entry_bar_index(strategy.opentrades - 1) if strategy.opentrades > 0 else na

    def BSLEx():
        return bar_index - strategy.closedtrades.exit_bar_index(strategy.closedtrades - 1) if strategy.opentrades == 0 else na

    if strategy.netprofit > 0 and reinvest:
        trade_amount = math.floor((strategy.initial_capital + profit * reinvest_percent * 0.01) * margin_req / close)
    else:
        trade_amount = math.floor(strategy.initial_capital * margin_req / close)
    percentage = iPercent * 0.01
    datr = request.security(syminfo.tickerid, '1D', ta.rma(ta.tr, atrlen))
    datrp = datr * percentage
    atr = ta.rma(ta.tr, atrlen)
    pm_t = time(timeframe.period, pm_session)
    pm_h: Persistent[float] = 0.0
    pm_l: Persistent[float] = 9999.9
    if cast_bool(pm_t):
        pm_h = high if high > pm_h else pm_h
        pm_l = low if low < pm_l else pm_l
    pm_range = pm_h - pm_l
    bgcolor(color.new(color.white, 95) if cast_bool(pm_t) else na)
    rsi1 = ta.rsi(src, lengthRSI)
    k = ta.sma(ta.stoch(rsi1, rsi1, rsi1, lengthStoch), smoothK)
    d: Series = ta.sma(k, smoothD)
    def ma(source, length, type):
        __block_result__ = na
        __switch__ = type
        if __switch__ == 'SMA':
            __block_result__ = ta.sma(source, length)
        elif __switch__ == 'Bollinger Bands':
            __block_result__ = ta.sma(source, length)
        elif __switch__ == 'EMA':
            __block_result__ = ta.ema(source, length)
        elif __switch__ == 'SMMA (RMA)':
            __block_result__ = ta.rma(source, length)
        elif __switch__ == 'WMA':
            __block_result__ = ta.wma(source, length)
        elif __switch__ == 'VWMA':
            __block_result__ = ta.vwma(source, length)
        return __block_result__

    up = ta.rma(math.max(ta.change(src), 0), len)
    down = ta.rma(-math.min(ta.change(src), 0), len)
    rsi = 100 if down == 0 else 0 if up == 0 else 100 - 100 / (1 + up / down)
    rsiSM = ta.sma(rsi, len2)
    rsiMA = ma(rsi, malen, maType)
    rsi_bull = rsiSM > rsiMA and rsi > 50 and (rsi > rsiSM)
    rsi_bear = rsiSM < rsiMA and rsi < 50 and (rsi < rsiSM)
    trend: Persistent[int] = 0
    if cast_bool(pm_t):
        trend = 0
    else:
        trend = (1 if close > pm_h else -1 if close < pm_l else 0) if trend == 0 else trend
    plot(trend, 'Trade direction')
    plot(pm_h if cast_bool(time(timeframe.period, '0930-1600:23456')) or cast_bool(pm_t) else high, title='PM High', color=color.blue if cast_bool(time(timeframe.period, '0930-1600:23456')) or cast_bool(pm_t) else color.new(color.black, 100), linewidth=2, trackprice=True)
    plot(pm_l if cast_bool(time(timeframe.period, '0930-1600:23456')) or cast_bool(pm_t) else low, title='PM Low', color=color.orange if cast_bool(time(timeframe.period, '0930-1600:23456')) or cast_bool(pm_t) else color.new(color.black, 100), linewidth=2, trackprice=True)
    traded: Persistent[bool] = False
    crossover_1 = ta.crossover(k, d)
    L_entry1 = trend == 1 and traded == False and (d[1] < stoch_l_limit) and crossover_1
    crossunder_1 = ta.crossunder(k, d)
    S_entry1 = trend == -1 and traded == False and (d[1] > stoch_h_limit) and crossunder_1
    if L_entry1 and window:
        strategy.entry('Long', strategy.long, trade_amount)
        traded = True
    if S_entry1 and window:
        strategy.entry('Short', strategy.short, trade_amount)
        traded = True
    entry_price = strategy.opentrades.entry_price(0)
    L_SL = pm_l - datrp if entry_price > pm_h else entry_price - pm_range - datrp
    S_SL = pm_h + datrp if entry_price < pm_l else entry_price + pm_range + datrp
    L_risk = entry_price - L_SL
    S_risk = S_SL - entry_price
    L_PT = entry_price + L_risk * RRR
    S_PT = entry_price - S_risk * RRR
    p0 = plot(close if strategy.opentrades.size(0) == 0 else entry_price, 'Entry Price', color=na if strategy.opentrades.size(0) == 0 else color.gray, linewidth=1)
    BSLE_1 = BSLE()
    p1 = plot(L_SL if strategy.opentrades.size(0) > 0 else low, 'Long SL', color=color.red if (cast_bool(t1) or cast_bool(pm_t)) and strategy.opentrades.size(0) > 0 and (BSLE_1 > 0) else color.new(color.black, 100), linewidth=3)
    BSLE_2 = BSLE()
    p2 = plot(L_PT if strategy.opentrades.size(0) > 0 else high, 'Long PT', color=color.green if (cast_bool(t1) or cast_bool(pm_t)) and strategy.opentrades.size(0) > 0 and (BSLE_2 > 0) else color.new(color.black, 100), linewidth=3)
    BSLE_3 = BSLE()
    p3 = plot(S_SL if strategy.opentrades.size(0) < 0 else high, 'Long SL', color=color.red if (cast_bool(t1) or cast_bool(pm_t)) and strategy.opentrades.size(0) < 0 and (BSLE_3 > 0) else color.new(color.black, 100), linewidth=3)
    BSLE_4 = BSLE()
    p4 = plot(S_PT if strategy.opentrades.size(0) < 0 else low, 'Long PT', color=color.green if (cast_bool(t1) or cast_bool(pm_t)) and strategy.opentrades.size(0) < 0 and (BSLE_4 > 0) else color.new(color.black, 100), linewidth=3)
    fill(p1, p0, color.new(color.red, 95))
    fill(p2, p0, color.new(color.green, 95))
    fill(p3, p0, color.new(color.red, 95))
    fill(p4, p0, color.new(color.green, 95))
    L_exit1 = d > 80 and strategy.opentrades.profit(0) <= 0 and rsi_bear
    S_exit1 = d < 20 and strategy.opentrades.profit(0) <= 0 and rsi_bull
    if strategy.opentrades.size(0) > 0:
        strategy.exit('Exit', 'Long', limit=L_PT, stop=L_SL)
        if L_exit1:
            strategy.close('Long', comment='Exit Early')
    if strategy.opentrades.size(0) < 0:
        strategy.exit('Exit', 'Short', limit=S_PT, stop=S_SL)
        if S_exit1:
            strategy.close('Short', comment='Exit Early')
    time_1 = time(timeframe.period, '0755-0800:23456')
    if cast_bool(time(timeframe.period, '1555-1600:23456')) or cast_bool(time_1):
        strategy.close_all()
        traded = False
        pm_h = 0.0
        pm_l = 9999.9


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
